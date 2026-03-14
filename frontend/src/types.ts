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

export interface QuarterAdvanceResponse {
  quarter: string;
  changes: ChangeRecord[];
  next_quarter: string;
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
