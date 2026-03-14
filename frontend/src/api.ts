import type {
  CompanyOverview,
  EnhancedModeSettings,
  FitResult,
  GraphResponse,
  PersonDetail,
  PersonSummary,
  PlacementResponse,
  QuarterAdvanceResponse,
  ScoringWeights,
  SimulationStatus,
} from "./types";

const BASE = "/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path}: ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`POST ${path}: ${res.status}`);
  return res.json();
}

async function put<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`PUT ${path}: ${res.status}`);
  return res.json();
}

export const api = {
  getCompany: () => get<CompanyOverview>("/company"),
  getPeople: () => get<PersonSummary[]>("/people"),
  getPerson: (id: string) => get<PersonDetail>(`/people/${id}`),
  evaluatePerson: (id: string) => get<FitResult[]>(`/people/${id}/evaluate`),

  getSimStatus: () => get<SimulationStatus>("/simulation/status"),
  advanceQuarter: () => post<QuarterAdvanceResponse>("/simulation/advance"),
  placePerson: (personId: string, roleId: string, departmentId: string) =>
    post<PlacementResponse>("/simulation/place", {
      person_id: personId,
      role_id: roleId,
      department_id: departmentId,
    }),
  previewPlace: (personId: string, roleId: string, departmentId: string) =>
    post<FitResult>("/simulation/preview-place", {
      person_id: personId,
      role_id: roleId,
      department_id: departmentId,
    }),
  rollback: (steps: number) =>
    post<{ rolled_back_to: string; history_length: number }>(
      "/simulation/rollback",
      { steps },
    ),
  resetSimulation: () => post<SimulationStatus>("/simulation/reset"),
  setEnhancedMode: (settings: EnhancedModeSettings) =>
    put<SimulationStatus>("/simulation/enhanced", settings),

  getGraph: () => get<GraphResponse>("/graph"),

  getWeights: () => get<ScoringWeights>("/weights"),
  updateWeights: (w: ScoringWeights) => put<ScoringWeights>("/weights", w),
};
