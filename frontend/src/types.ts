export interface PersonSummary {
  id: string;
  name: string;
  tenure_years: number;
  skill_count: number;
  active_role: string | null;
  active_department: string | null;
  burnout_risk: number;
  morale: number;
  potential: number;
  departed: boolean;
}

export interface SkillInfo {
  id: string;
  name: string;
  category: string;
  person_level: string | null;
  person_years: number | null;
  potential_level: string | null;
  quarters_active: number;
  quarters_idle: number;
  required_level: string | null;
  weight: number | null;
}

export interface FitResult {
  person_id: string;
  person_name: string;
  department_id: string;
  department_name: string;
  role_id: string;
  role_title: string;
  skill_match_score: number;
  historical_score: number;
  level_match_score: number;
  burnout_risk_score: number;
  fit_score: number;
  predicted_performance: number;
  breakdown: Record<string, number>;
}

export interface PersonDetail {
  id: string;
  name: string;
  tenure_years: number;
  skills: SkillInfo[];
  active_role: string | null;
  active_department: string | null;
  burnout_risk: number;
  morale: number;
  potential: number;
  learning_rate: number;
  departed: boolean;
  fit_results: FitResult[];
}

export interface CompanyOverview {
  name: string;
  people_count: number;
  department_count: number;
  role_count: number;
  skill_count: number;
  avg_tenure: number;
  avg_burnout_risk: number;
}

export interface ChangeRecord {
  person_id: string;
  person_name: string;
  change_type: string;
  description: string;
  old_value: string | null;
  new_value: string | null;
  role_title?: string;
  department_name?: string;
  rating?: string;
  predicted_performance?: number;
}

export interface SimulationStatus {
  current_quarter: string;
  history_length: number;
  people_count: number;
  active_people: number;
  departed_people: number;
  average_morale: number;
  enhanced_mode: boolean;
}

export interface ScoringWeights {
  skill_match: number;
  historical_performance: number;
  level_match: number;
  burnout_risk: number;
}

export interface EnhancedModeSettings {
  enhanced: boolean;
  growth: boolean;
  morale: boolean;
  attrition: boolean;
  events: boolean;
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  data: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface PlacementResponse {
  person_name: string;
  role_title: string;
  department_name: string;
  previous_role_title: string | null;
}

export interface DepartmentSummary {
  id: string;
  name: string;
  role_count: number;
  member_count: number;
}

// ── Explainer types ──

export interface VariableDefinition {
  symbol: string;
  name_ko: string;
  name_en: string;
  range: string;
  description_ko: string;
  description_en: string;
}

export interface ConstantDefinition {
  symbol: string;
  name_en: string;
  value: string;
  description_ko: string;
  description_en: string;
  source: string;
}

export interface FormulaDefinition {
  id: string;
  name_ko: string;
  name_en: string;
  formula_plain: string;
  description_ko: string;
  description_en: string;
  variables: VariableDefinition[];
  constants: ConstantDefinition[];
  theoretical_basis: string;
  theoretical_basis_ko: string;
  category: string;
  related_formulas: string[];
}

export interface GlossaryEntry {
  id: string;
  term_ko: string;
  term_en: string;
  definition_ko: string;
  definition_en: string;
  category: string;
}

export interface ScoreStep {
  step_number: number;
  component: string;
  component_ko: string;
  formula_applied: string;
  inputs: Record<string, unknown>;
  intermediate_value: number;
  weight: number;
  weighted_value: number;
  explanation_ko: string;
  explanation_en: string;
}

export interface ScoreBreakdown {
  person_id: string;
  person_name: string;
  role_id: string;
  role_title: string;
  department_id: string;
  department_name: string;
  steps: ScoreStep[];
  final_fit_score: number;
  final_predicted_performance: number;
  summary_ko: string;
  summary_en: string;
}

// ── Game types ──

export interface CompanyScore {
  total: number;
  team_performance: number;
  morale_health: number;
  retention_rate: number;
  skill_coverage: number;
  growth_rate: number;
}

export interface PersonHighlight {
  person_id: string;
  person_name: string;
  highlight_type: string;
  description: string;
  description_ko: string;
  metric_value: number | null;
}

export interface Headline {
  icon: string;
  text: string;
  text_ko: string;
  category: string;
}

export interface DepartmentScoreEntry {
  department_id: string;
  department_name: string;
  avg_rating: number;
  active_count: number;
  departed_count: number;
}

export interface QuarterReport {
  quarter: string;
  company_score: CompanyScore;
  previous_score: number | null;
  score_delta: number | null;
  headlines: Headline[];
  mvp: PersonHighlight | null;
  warnings: PersonHighlight[];
  highlights: PersonHighlight[];
  department_scores: DepartmentScoreEntry[];
  total_active: number;
  total_departed: number;
  avg_morale: number;
  growth_events: number;
  decay_events: number;
  departures_this_quarter: number;
}

export interface Achievement {
  id: string;
  name: string;
  name_ko: string;
  description: string;
  description_ko: string;
  icon: string;
  category: string;
  unlocked: boolean;
  unlocked_at: string | null;
}

export interface AchievementProgress {
  unlocked: number;
  total: number;
  percentage: number;
  quarters_completed: number;
}

export interface GameAdvanceResponse {
  quarter: string;
  changes: ChangeRecord[];
  report: QuarterReport;
  newly_unlocked: Achievement[];
  achievement_progress: AchievementProgress;
  next_quarter: string;
}

export interface ScoreHistoryEntry {
  quarter: string;
  total: number;
  team_performance: number;
  morale_health: number;
  retention_rate: number;
  skill_coverage: number;
  growth_rate: number;
}

// ── Recommendation types ──

export interface Recommendation {
  person_id: string;
  person_name: string;
  role_id: string;
  role_title: string;
  department_id: string;
  department_name: string;
  fit_score: number;
  predicted_performance: number;
  strengths: string[];
  gaps: string[];
  growth_potential: string;
  recommendation_en: string;
  recommendation_ko: string;
}

export interface PlacementCell {
  person_id: string;
  person_name: string;
  role_id: string;
  role_title: string;
  department_id: string;
  department_name: string;
  fit_score: number;
}

// ── Company Profile types ──

export interface IndustryTemplate {
  industry: string;
  name_ko: string;
  name_en: string;
  description_ko: string;
  description_en: string;
  departments: string[];
  roles: string[];
  skills: string[];
}

export interface CompanyCreateRequest {
  name: string;
  industry: string;
  growth_stage: string;
  culture_type: string;
  num_people: number;
  seed?: number;
}

// ── Estimation (Bayesian Skill Assessment) ─────────────────────────

export interface Project {
  id: string;
  name: string;
  description: string;
  difficulty: number;
  required_skill_ids: string[];
  start_date: string;
  end_date: string | null;
  status: string;
  assignment_count?: number;
  outcome_count?: number;
}

export interface ProjectDetail extends Project {
  required_skills: { id: string; name: string }[];
  assignments: {
    id: string;
    person_id: string;
    person_name: string;
    role: string;
  }[];
  outcomes: {
    id: string;
    person_id: string;
    person_name: string;
    result: number;
    result_label: string;
    evaluated_at: string;
    notes: string;
  }[];
}

export interface SkillEstimate {
  skill_id: string;
  skill_name: string;
  mu: number;
  sigma: number;
  confidence: number;
  discrete_level: number;
  level_name: string;
  trend: string;
  update_count: number;
  official_level: number | null;
}

export interface ScoutReport {
  person_id: string;
  person_name: string;
  estimates: SkillEstimate[];
  avg_confidence: number;
  total_projects: number;
}

export interface ImportSummary {
  imported_count: number;
  employees: {
    name: string;
    position: string;
    department: string;
    hire_date: string;
  }[];
  errors: string[];
  warnings: string[];
}
