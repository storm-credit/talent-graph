import { create } from "zustand";
import type {
  ChangeRecord,
  GameAdvanceResponse,
  PersonSummary,
  SimulationStatus,
} from "../types";
import { api } from "../api";

export interface ActiveEffect {
  change: ChangeRecord;
  index: number;
}

type PlaybackState = "idle" | "loading" | "playing" | "paused" | "finished";
type Speed = 1 | 2 | 4;

interface GameModeStore {
  // People
  people: PersonSummary[];
  departmentGroups: Record<string, PersonSummary[]>;

  // Simulation status
  simStatus: SimulationStatus | null;

  // Playback
  playbackState: PlaybackState;
  speed: Speed;
  currentChangeIndex: number;
  totalChanges: number;
  activeEffects: Record<string, ActiveEffect>; // person_id -> effect
  activeBanner: ChangeRecord | null;
  processedChanges: ChangeRecord[];

  // Result
  advanceResult: GameAdvanceResponse | null;
  localPeople: Record<string, PersonSummary>; // mutated copy

  // Internal
  _timerId: ReturnType<typeof setTimeout> | null;

  // Actions
  fetchPeople: () => Promise<void>;
  fetchStatus: () => Promise<void>;
  startQuarter: () => Promise<void>;
  setSpeed: (s: Speed) => void;
  pause: () => void;
  resume: () => void;
  skipToEnd: () => void;
  dismissSummary: () => void;
  resetGame: () => Promise<void>;
  _playNext: () => void;
}

function groupByDept(people: PersonSummary[]): Record<string, PersonSummary[]> {
  const groups: Record<string, PersonSummary[]> = {};
  for (const p of people) {
    const dept = p.active_department || "Unassigned";
    if (!groups[dept]) groups[dept] = [];
    groups[dept].push(p);
  }
  return groups;
}

export const useGameModeStore = create<GameModeStore>((set, get) => ({
  people: [],
  departmentGroups: {},
  simStatus: null,

  playbackState: "idle",
  speed: 1,
  currentChangeIndex: 0,
  totalChanges: 0,
  activeEffects: {},
  activeBanner: null,
  processedChanges: [],

  advanceResult: null,
  localPeople: {},
  _timerId: null,

  fetchPeople: async () => {
    const people = await api.getPeople();
    const active = people.filter((p) => !p.departed);
    const localPeople: Record<string, PersonSummary> = {};
    for (const p of active) localPeople[p.id] = { ...p };
    set({
      people: active,
      departmentGroups: groupByDept(active),
      localPeople,
    });
  },

  fetchStatus: async () => {
    const simStatus = await api.getSimStatus();
    set({ simStatus });
  },

  startQuarter: async () => {
    const state = get();
    if (state.playbackState === "loading" || state.playbackState === "playing")
      return;

    set({ playbackState: "loading", activeEffects: {}, activeBanner: null, processedChanges: [] });

    try {
      const result = await api.gameAdvance();
      const simStatus = await api.getSimStatus();

      // Reset local people from current state
      const people = await api.getPeople();
      const active = people.filter((p) => !p.departed);
      const localPeople: Record<string, PersonSummary> = {};
      // Use PRE-change state for animation - we'll mutate as changes play
      for (const p of get().people) localPeople[p.id] = { ...p };

      set({
        advanceResult: result,
        simStatus,
        totalChanges: result.changes.length,
        currentChangeIndex: 0,
        playbackState: "playing",
        people: active,
      });

      // Start playback
      get()._playNext();
    } catch (e) {
      console.error(e);
      set({ playbackState: "idle" });
    }
  },

  _playNext: () => {
    const state = get();
    if (state.playbackState !== "playing") return;
    if (!state.advanceResult) return;

    const idx = state.currentChangeIndex;
    if (idx >= state.advanceResult.changes.length) {
      // All changes played - update people to final state
      const people = get().people;
      set({
        playbackState: "finished",
        activeEffects: {},
        activeBanner: null,
        departmentGroups: groupByDept(people.filter((p) => !p.departed)),
      });
      return;
    }

    const change = state.advanceResult.changes[idx];
    const baseDelay = 800 / state.speed;

    // Set active effect for this person
    const newEffects = { ...state.activeEffects };
    newEffects[change.person_id] = { change, index: idx };

    // For events, set banner
    const isBanner = change.change_type === "event";

    // Apply change to local people state
    const localPeople = { ...state.localPeople };
    const person = localPeople[change.person_id];
    if (person) {
      if (change.change_type === "morale_change" && change.new_value) {
        person.morale = parseFloat(change.new_value);
      } else if (change.change_type === "burnout_change" && change.new_value) {
        person.burnout_risk = parseFloat(change.new_value);
      } else if (change.change_type === "departure") {
        person.departed = true;
      }
      localPeople[change.person_id] = { ...person };
    }

    set({
      activeEffects: newEffects,
      activeBanner: isBanner ? change : state.activeBanner,
      currentChangeIndex: idx + 1,
      localPeople,
      processedChanges: [...state.processedChanges, change],
    });

    // Clear effect after animation, then play next
    const effectDuration = Math.max(600 / state.speed, 300);
    setTimeout(() => {
      const s = get();
      const effects = { ...s.activeEffects };
      if (effects[change.person_id]?.index === idx) {
        delete effects[change.person_id];
      }
      set({ activeEffects: effects });
      if (isBanner) {
        setTimeout(() => set({ activeBanner: null }), 400 / s.speed);
      }
    }, effectDuration);

    const timerId = setTimeout(() => get()._playNext(), baseDelay);
    set({ _timerId: timerId });
  },

  setSpeed: (speed) => set({ speed }),

  pause: () => {
    const { _timerId } = get();
    if (_timerId) clearTimeout(_timerId);
    set({ playbackState: "paused", _timerId: null });
  },

  resume: () => {
    set({ playbackState: "playing" });
    get()._playNext();
  },

  skipToEnd: () => {
    const { _timerId, advanceResult } = get();
    if (_timerId) clearTimeout(_timerId);
    if (!advanceResult) return;

    // Apply all remaining changes
    const localPeople = { ...get().localPeople };
    for (const change of advanceResult.changes) {
      const person = localPeople[change.person_id];
      if (person) {
        if (change.change_type === "morale_change" && change.new_value)
          person.morale = parseFloat(change.new_value);
        if (change.change_type === "burnout_change" && change.new_value)
          person.burnout_risk = parseFloat(change.new_value);
        if (change.change_type === "departure") person.departed = true;
        localPeople[change.person_id] = { ...person };
      }
    }

    const people = get().people;
    set({
      playbackState: "finished",
      currentChangeIndex: advanceResult.changes.length,
      totalChanges: advanceResult.changes.length,
      activeEffects: {},
      activeBanner: null,
      localPeople,
      processedChanges: advanceResult.changes,
      departmentGroups: groupByDept(people.filter((p) => !p.departed)),
      _timerId: null,
    });
  },

  dismissSummary: () => {
    const people = get().people;
    set({
      playbackState: "idle",
      advanceResult: null,
      processedChanges: [],
      departmentGroups: groupByDept(people.filter((p) => !p.departed)),
    });
  },

  resetGame: async () => {
    const { _timerId } = get();
    if (_timerId) clearTimeout(_timerId);
    await api.resetSimulation();
    const [people, simStatus] = await Promise.all([
      api.getPeople(),
      api.getSimStatus(),
    ]);
    const active = people.filter((p) => !p.departed);
    const localPeople: Record<string, PersonSummary> = {};
    for (const p of active) localPeople[p.id] = { ...p };
    set({
      people: active,
      departmentGroups: groupByDept(active),
      localPeople,
      simStatus,
      playbackState: "idle",
      currentChangeIndex: 0,
      totalChanges: 0,
      activeEffects: {},
      activeBanner: null,
      processedChanges: [],
      advanceResult: null,
      _timerId: null,
    });
  },
}));
