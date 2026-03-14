import type {
  Achievement,
  AchievementProgress,
  CompanyCreateRequest,
  CompanyOverview,
  CompanyScore,
  EnhancedModeSettings,
  FitResult,
  FormulaDefinition,
  GameAdvanceResponse,
  GlossaryEntry,
  GraphResponse,
  IndustryTemplate,
  PersonDetail,
  PersonSummary,
  PlacementCell,
  PlacementResponse,
  QuarterReport,
  Recommendation,
  ScoreBreakdown,
  ScoreHistoryEntry,
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
  getSimConfig: () => get<Record<string, unknown>>("/simulation/config"),
  updateSimConfig: (config: Record<string, unknown>) =>
    put<Record<string, unknown>>("/simulation/config", config),

  getGraph: () => get<GraphResponse>("/graph"),

  getWeights: () => get<ScoringWeights>("/weights"),
  updateWeights: (w: ScoringWeights) => put<ScoringWeights>("/weights", w),

  // Explainer
  getFormulas: () => get<FormulaDefinition[]>("/explainer/formulas"),
  getGlossary: () => get<GlossaryEntry[]>("/explainer/glossary"),
  getBreakdown: (personId: string, roleId: string, deptId: string) =>
    get<ScoreBreakdown>(`/explainer/breakdown/${personId}/${roleId}/${deptId}`),

  // Game
  getCompanyScore: () => get<CompanyScore>("/game/score"),
  getScoreHistory: () => get<ScoreHistoryEntry[]>("/game/score/history"),
  getAchievements: () =>
    get<{ achievements: Achievement[]; progress: AchievementProgress }>(
      "/game/achievements",
    ),
  getUnlockedAchievements: () => get<Achievement[]>("/game/achievements/unlocked"),
  gameAdvance: () => post<GameAdvanceResponse>("/game/advance"),
  getLatestReport: () => get<QuarterReport>("/game/report/latest"),

  // Recommendations
  getRecommendationsForPerson: (id: string) =>
    get<Recommendation[]>(`/recommendations/person/${id}`),
  getRecommendationsForRole: (roleId: string, deptId: string) =>
    get<Recommendation[]>(`/recommendations/role/${roleId}/${deptId}`),
  getPlacementMatrix: () => get<PlacementCell[]>("/recommendations/matrix"),

  // Company Profile
  getTemplates: () => get<IndustryTemplate[]>("/company-profile/templates"),
  getTemplate: (industry: string) =>
    get<IndustryTemplate>(`/company-profile/templates/${industry}`),
  createCompany: (req: CompanyCreateRequest) =>
    post<CompanyOverview>("/company-profile/create", req),
};
