import { create } from "zustand";
import type {
  ChangeRecord,
  QuarterAdvanceResponse,
  SimulationStatus,
} from "../types";
import { api } from "../api";

interface SimulationStore {
  status: SimulationStatus | null;
  lastAdvance: QuarterAdvanceResponse | null;
  allChanges: ChangeRecord[];
  loading: boolean;

  fetchStatus: () => Promise<void>;
  advance: () => Promise<QuarterAdvanceResponse>;
  rollback: (steps: number) => Promise<void>;
  reset: () => Promise<void>;
}

export const useSimulationStore = create<SimulationStore>((set, get) => ({
  status: null,
  lastAdvance: null,
  allChanges: [],
  loading: false,

  fetchStatus: async () => {
    const status = await api.getSimStatus();
    set({ status });
  },

  advance: async () => {
    set({ loading: true });
    const result = await api.advanceQuarter();
    const status = await api.getSimStatus();
    set((s) => ({
      status,
      lastAdvance: result,
      allChanges: [...s.allChanges, ...result.changes],
      loading: false,
    }));
    return result;
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
    set({ status, lastAdvance: null, allChanges: [], loading: false });
  },
}));
