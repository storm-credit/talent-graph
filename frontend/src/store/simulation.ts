import { create } from "zustand";
import type {
  Achievement,
  AchievementProgress,
  ChangeRecord,
  GameAdvanceResponse,
  ScoreHistoryEntry,
  SimulationStatus,
} from "../types";
import { api } from "../api";

interface SimulationStore {
  status: SimulationStatus | null;
  lastAdvance: GameAdvanceResponse | null;
  allChanges: ChangeRecord[];
  loading: boolean;

  // Quarter report & analytics data
  showReport: boolean;
  scoreHistory: ScoreHistoryEntry[];
  achievements: Achievement[];
  achievementProgress: AchievementProgress | null;

  fetchStatus: () => Promise<void>;
  advance: () => Promise<GameAdvanceResponse>;
  rollback: (steps: number) => Promise<void>;
  reset: () => Promise<void>;
  closeReport: () => void;
  fetchAnalyticsData: () => Promise<void>;
}

export const useSimulationStore = create<SimulationStore>((set, get) => ({
  status: null,
  lastAdvance: null,
  allChanges: [],
  loading: false,

  showReport: false,
  scoreHistory: [],
  achievements: [],
  achievementProgress: null,

  fetchStatus: async () => {
    const status = await api.getSimStatus();
    set({ status });
  },

  fetchAnalyticsData: async () => {
    try {
      const [achData, history] = await Promise.all([
        api.getAchievements(),
        api.getScoreHistory(),
      ]);
      set({
        achievements: achData.achievements,
        achievementProgress: achData.progress,
        scoreHistory: history,
      });
    } catch {
      // Analytics data not available yet (no quarters simulated)
    }
  },

  advance: async () => {
    set({ loading: true });
    try {
      // Unified advance: returns changes + report + achievements
      const result = await api.gameAdvance();
      const status = await api.getSimStatus();

      // Update achievements with newly unlocked
      const currentAch = get().achievements;
      const updatedAch = currentAch.map((a) => {
        const unlocked = result.newly_unlocked.find((u) => u.id === a.id);
        return unlocked
          ? { ...a, unlocked: true, unlocked_at: unlocked.unlocked_at }
          : a;
      });

      // Build score history entry
      const h = result.report.company_score;
      const newEntry: ScoreHistoryEntry = {
        quarter: result.report.quarter,
        total: h.total,
        team_performance: h.team_performance,
        morale_health: h.morale_health,
        retention_rate: h.retention_rate,
        skill_coverage: h.skill_coverage,
        growth_rate: h.growth_rate,
      };

      set((s) => ({
        status,
        lastAdvance: result,
        allChanges: [...s.allChanges, ...result.changes],
        loading: false,
        showReport: true,
        achievements: updatedAch,
        achievementProgress: result.achievement_progress,
        scoreHistory: [...s.scoreHistory, newEntry],
      }));
      return result;
    } catch (e) {
      set({ loading: false });
      throw e;
    }
  },

  rollback: async (steps) => {
    set({ loading: true });
    await api.rollback(steps);
    const status = await api.getSimStatus();
    set({ status, loading: false });
  },

  reset: async () => {
    set({ loading: true });
    await api.resetSimulation();
    const status = await api.getSimStatus();
    set({
      status,
      lastAdvance: null,
      allChanges: [],
      loading: false,
      showReport: false,
      scoreHistory: [],
      achievements: [],
      achievementProgress: null,
    });
    // Re-fetch analytics data (achievements reset)
    get().fetchAnalyticsData();
  },

  closeReport: () => set({ showReport: false }),
}));
