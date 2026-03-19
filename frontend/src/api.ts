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
  ImportSummary,
  IndustryTemplate,
  PersonDetail,
  PersonSummary,
  PlacementCell,
  PlacementResponse,
  Project,
  ProjectDetail,
  QuarterReport,
  Recommendation,
  ScoreBreakdown,
  ScoreHistoryEntry,
  ScoringWeights,
  ScoutReport,
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

  // Estimation (Bayesian Skill Assessment)
  getProjects: () => get<Project[]>("/estimation/projects"),
  getProject: (id: string) => get<ProjectDetail>(`/estimation/projects/${id}`),
  createProject: (req: {
    name: string;
    description?: string;
    difficulty: number;
    required_skill_ids: string[];
    start_date?: string;
    end_date?: string;
  }) => post<{ id: string }>("/estimation/projects", req),
  deleteProject: (id: string) =>
    fetch(`${BASE}/estimation/projects/${id}`, { method: "DELETE" }).then((r) =>
      r.json(),
    ),
  assignToProject: (projectId: string, personId: string, role: string) =>
    post(`/estimation/projects/${projectId}/assign`, {
      person_id: personId,
      role,
    }),
  recordOutcome: (
    projectId: string,
    personId: string,
    result: number,
    notes?: string,
  ) =>
    post(`/estimation/projects/${projectId}/outcome`, {
      person_id: personId,
      result,
      notes: notes || "",
    }),
  getScoutReport: (personId: string) =>
    get<ScoutReport>(`/estimation/people/${personId}/estimates`),
  initializeEstimates: () => post("/estimation/initialize-all"),
  importCsv: async (file: File): Promise<ImportSummary> => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE}/estimation/import`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) throw new Error(`Import failed: ${res.status}`);
    return res.json();
  },
};
