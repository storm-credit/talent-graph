import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  BookOpen,
  ChevronDown,
  ChevronRight,
  Search,
  FlaskConical,
  Workflow,
  Library,
  Microscope,
} from "lucide-react";
import { api } from "../api";
import type {
  FormulaDefinition,
  GlossaryEntry,
  PersonSummary,
  ScoreBreakdown,
  ScoreStep,
  FitResult,
} from "../types";

// ── Tab definitions ──

const tabs = [
  { id: "pipeline", label: "작동 원리", icon: Workflow },
  { id: "formulas", label: "공식 레퍼런스", icon: FlaskConical },
  { id: "glossary", label: "용어 사전", icon: Library },
  { id: "try-it", label: "직접 해보기", icon: Microscope },
] as const;

type TabId = (typeof tabs)[number]["id"];

export function HowItWorksPage() {
  const [activeTab, setActiveTab] = useState<TabId>("pipeline");

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <BookOpen className="text-emerald-400" size={24} />
        <div>
          <h1 className="text-xl font-bold text-zinc-100">
            어떻게 작동하나요?
          </h1>
          <p className="text-sm text-zinc-500">
            TalentGraph 알고리즘의 원리와 공식을 설명합니다
          </p>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 bg-zinc-900 p-1 rounded-xl border border-zinc-800">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === id
                ? "bg-emerald-500/15 text-emerald-400 shadow-sm"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
            }`}
          >
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === "pipeline" && <PipelineTab />}
          {activeTab === "formulas" && <FormulasTab />}
          {activeTab === "glossary" && <GlossaryTab />}
          {activeTab === "try-it" && <TryItTab />}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

// ── Pipeline Tab ──

const pipelineSteps = [
  {
    id: "input",
    title: "사람 (Person)",
    titleEn: "Person",
    color: "bg-blue-500/15 border-blue-500/30 text-blue-400",
    description: "스킬, 경력, 재직기간, 성과이력",
  },
  {
    id: "skill_match",
    title: "스킬 매칭",
    titleEn: "Skill Match",
    color: "bg-emerald-500/15 border-emerald-500/30 text-emerald-400",
    description: "보유 스킬 vs 역할 요구 스킬 비교",
    weight: "40%",
    formula: "min(person_level / required_level, 1.0) × weight",
    reference: "Boyatzis (1982)",
  },
  {
    id: "historical",
    title: "이력 성과",
    titleEn: "Historical Performance",
    color: "bg-amber-500/15 border-amber-500/30 text-amber-400",
    description: "과거 평가를 시간 가중 평균 (반감기 2년)",
    weight: "30%",
    formula: "Σ(rating × decay × role_boost) / Σ(weights)",
    reference: "Murphy & Cleveland (1995)",
  },
  {
    id: "level_match",
    title: "레벨 매칭",
    titleEn: "Level Match",
    color: "bg-violet-500/15 border-violet-500/30 text-violet-400",
    description: "현재 레벨과 역할 레벨의 갭 패널티",
    weight: "15%",
    formula: "max(0, 1.0 - (gap - 1) × 0.2)",
    reference: "Benson et al. (2019)",
  },
  {
    id: "burnout",
    title: "번아웃 리스크",
    titleEn: "Burnout Risk",
    color: "bg-red-500/15 border-red-500/30 text-red-400",
    description: "정체기간(60%) + 성과하락(40%) 복합 지표",
    weight: "-15%",
    formula: "0.6 × staleness + 0.4 × decline",
    reference: "Maslach & Leiter (2016)",
  },
  {
    id: "output",
    title: "적합도 점수",
    titleEn: "FitScore",
    color: "bg-emerald-500/15 border-emerald-500/30 text-emerald-400",
    description: "0~100% 최종 적합도 + 예측 성과 (1~5)",
  },
];

function PipelineTab() {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6">
        <h2 className="text-lg font-semibold text-zinc-100 mb-4">
          스코어링 파이프라인
        </h2>
        <p className="text-sm text-zinc-400 mb-6">
          TalentGraph는 4가지 요소를 가중 합산하여 사람-역할 적합도를 계산합니다.
          각 단계를 클릭하면 상세 설명을 볼 수 있습니다.
        </p>

        <div className="flex flex-col items-center gap-2">
          {pipelineSteps.map((step, i) => (
            <div key={step.id} className="w-full max-w-xl">
              <motion.button
                onClick={() =>
                  setExpanded(expanded === step.id ? null : step.id)
                }
                className={`w-full text-left p-4 rounded-xl border transition-all ${step.color} hover:scale-[1.01]`}
                whileTap={{ scale: 0.99 }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm">
                        {step.title}
                      </span>
                      <span className="text-xs opacity-60">
                        {step.titleEn}
                      </span>
                      {step.weight && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-300">
                          {step.weight}
                        </span>
                      )}
                    </div>
                    <p className="text-xs mt-1 opacity-70">
                      {step.description}
                    </p>
                  </div>
                  {step.formula && (
                    <ChevronDown
                      size={14}
                      className={`transition-transform ${
                        expanded === step.id ? "rotate-180" : ""
                      }`}
                    />
                  )}
                </div>
              </motion.button>

              <AnimatePresence>
                {expanded === step.id && step.formula && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="mx-4 p-4 bg-zinc-800/50 rounded-b-xl border border-t-0 border-zinc-700 space-y-2">
                      <div>
                        <span className="text-xs text-zinc-500">공식:</span>
                        <code className="block text-sm text-emerald-300 font-mono mt-1 bg-zinc-900 p-2 rounded">
                          {step.formula}
                        </code>
                      </div>
                      {step.reference && (
                        <div className="text-xs text-zinc-500">
                          학술 근거: {step.reference}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {i < pipelineSteps.length - 1 && (
                <div className="flex justify-center py-1">
                  <div className="w-0.5 h-4 bg-zinc-700" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Final formula box */}
        <div className="mt-6 p-4 bg-zinc-800 rounded-xl border border-zinc-700">
          <h3 className="text-sm font-semibold text-zinc-300 mb-2">
            최종 공식 (Final Formula)
          </h3>
          <code className="block text-sm text-emerald-300 font-mono">
            FitScore = 0.40×SkillMatch + 0.30×Historical + 0.15×LevelMatch -
            0.15×Burnout
          </code>
          <code className="block text-sm text-amber-300 font-mono mt-2">
            PredictedPerf = 1.0 + FitScore×4.0 + (Historical-0.5)×0.5 → [1, 5]
          </code>
          <p className="text-xs text-zinc-500 mt-2">
            Schmidt & Hunter (1998) — 인사 선발 타당도 메타분석에 기반한 가중치
          </p>
        </div>
      </div>
    </div>
  );
}

// ── Formulas Tab ──

const categoryLabels: Record<string, string> = {
  scoring: "스코어링",
  simulation: "시뮬레이션",
  growth: "스킬 성장",
  morale: "사기",
  attrition: "이직",
  events: "이벤트",
};

function FormulasTab() {
  const { data: formulas, isLoading } = useQuery({
    queryKey: ["formulas"],
    queryFn: api.getFormulas,
  });

  const [openId, setOpenId] = useState<string | null>(null);

  if (isLoading)
    return <div className="text-zinc-500 text-sm">로딩 중...</div>;

  const categories = [
    ...new Set((formulas || []).map((f) => f.category)),
  ];

  return (
    <div className="space-y-4">
      {categories.map((cat) => (
        <div
          key={cat}
          className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden"
        >
          <div className="px-4 py-3 border-b border-zinc-800">
            <h3 className="text-sm font-semibold text-zinc-300">
              {categoryLabels[cat] || cat}
            </h3>
          </div>
          <div className="divide-y divide-zinc-800">
            {(formulas || [])
              .filter((f) => f.category === cat)
              .map((f) => (
                <FormulaCard
                  key={f.id}
                  formula={f}
                  isOpen={openId === f.id}
                  onToggle={() =>
                    setOpenId(openId === f.id ? null : f.id)
                  }
                />
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function FormulaCard({
  formula,
  isOpen,
  onToggle,
}: {
  formula: FormulaDefinition;
  isOpen: boolean;
  onToggle: () => void;
}) {
  return (
    <div>
      <button
        onClick={onToggle}
        className="w-full text-left px-4 py-3 hover:bg-zinc-800/50 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm font-medium text-zinc-200">
              {formula.name_ko}
            </span>
            <span className="text-xs text-zinc-500 ml-2">
              {formula.name_en}
            </span>
          </div>
          <ChevronRight
            size={14}
            className={`text-zinc-500 transition-transform ${
              isOpen ? "rotate-90" : ""
            }`}
          />
        </div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-3">
              <code className="block text-sm text-emerald-300 font-mono bg-zinc-800 p-3 rounded-lg">
                {formula.formula_plain}
              </code>

              <p className="text-sm text-zinc-400">{formula.description_ko}</p>

              {formula.variables.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-zinc-500 mb-1">
                    변수
                  </h4>
                  <div className="space-y-1">
                    {formula.variables.map((v) => (
                      <div
                        key={v.symbol}
                        className="flex items-center gap-2 text-xs"
                      >
                        <code className="text-amber-300 font-mono w-8">
                          {v.symbol}
                        </code>
                        <span className="text-zinc-300">{v.name_ko}</span>
                        <span className="text-zinc-600">{v.range}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {formula.constants.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-zinc-500 mb-1">
                    상수
                  </h4>
                  <div className="space-y-1">
                    {formula.constants.map((c) => (
                      <div
                        key={c.symbol}
                        className="flex items-center gap-2 text-xs"
                      >
                        <code className="text-violet-300 font-mono w-8">
                          {c.symbol}
                        </code>
                        <span className="text-zinc-300">{c.name_en}</span>
                        <span className="text-zinc-500">= {c.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="text-xs text-zinc-600 pt-2 border-t border-zinc-800">
                {formula.theoretical_basis_ko}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Glossary Tab ──

function GlossaryTab() {
  const { data: glossary, isLoading } = useQuery({
    queryKey: ["glossary"],
    queryFn: api.getGlossary,
  });

  const [search, setSearch] = useState("");

  if (isLoading)
    return <div className="text-zinc-500 text-sm">로딩 중...</div>;

  const filtered = (glossary || []).filter(
    (g) =>
      g.term_ko.includes(search) ||
      g.term_en.toLowerCase().includes(search.toLowerCase()) ||
      g.definition_ko.includes(search),
  );

  const categories = [...new Set(filtered.map((g) => g.category))];

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500"
          size={14}
        />
        <input
          type="text"
          placeholder="용어 검색..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-emerald-500/50"
        />
      </div>

      {categories.map((cat) => (
        <div
          key={cat}
          className="bg-zinc-900 rounded-xl border border-zinc-800"
        >
          <div className="px-4 py-2 border-b border-zinc-800">
            <span className="text-xs font-semibold text-zinc-500 uppercase">
              {cat}
            </span>
          </div>
          <div className="divide-y divide-zinc-800">
            {filtered
              .filter((g) => g.category === cat)
              .map((g) => (
                <div key={g.id} className="px-4 py-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-zinc-200">
                      {g.term_ko}
                    </span>
                    <span className="text-xs text-zinc-500">{g.term_en}</span>
                  </div>
                  <p className="text-xs text-zinc-400">{g.definition_ko}</p>
                </div>
              ))}
          </div>
        </div>
      ))}

      <p className="text-xs text-zinc-600 text-center">
        총 {filtered.length}개 용어
      </p>
    </div>
  );
}

// ── Try It Tab ──

function TryItTab() {
  const { data: people } = useQuery({
    queryKey: ["people"],
    queryFn: api.getPeople,
  });

  const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null);
  const [selectedFit, setSelectedFit] = useState<FitResult | null>(null);

  // Load person detail to get fit results
  const { data: personDetail } = useQuery({
    queryKey: ["person", selectedPersonId],
    queryFn: () => api.getPerson(selectedPersonId!),
    enabled: !!selectedPersonId,
  });

  // Load breakdown when person + role selected
  const { data: breakdown, isLoading: breakdownLoading } = useQuery({
    queryKey: [
      "breakdown",
      selectedFit?.person_id,
      selectedFit?.role_id,
      selectedFit?.department_id,
    ],
    queryFn: () =>
      api.getBreakdown(
        selectedFit!.person_id,
        selectedFit!.role_id,
        selectedFit!.department_id,
      ),
    enabled: !!selectedFit,
  });

  const activePeople = (people || []).filter((p) => !p.departed);

  return (
    <div className="space-y-4">
      <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
        <h3 className="text-sm font-semibold text-zinc-300 mb-3">
          사람과 역할을 선택하면 단계별 점수 계산을 확인할 수 있습니다
        </h3>

        <div className="grid grid-cols-2 gap-4">
          {/* Person selector */}
          <div>
            <label className="text-xs text-zinc-500 mb-1 block">
              사람 선택
            </label>
            <select
              value={selectedPersonId || ""}
              onChange={(e) => {
                setSelectedPersonId(e.target.value || null);
                setSelectedFit(null);
              }}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-emerald-500/50"
            >
              <option value="">선택하세요</option>
              {activePeople.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          {/* Role selector */}
          <div>
            <label className="text-xs text-zinc-500 mb-1 block">
              역할 선택
            </label>
            <select
              value={
                selectedFit
                  ? `${selectedFit.role_id}|${selectedFit.department_id}`
                  : ""
              }
              onChange={(e) => {
                if (!e.target.value || !personDetail) {
                  setSelectedFit(null);
                  return;
                }
                const [roleId, deptId] = e.target.value.split("|");
                const fit = personDetail.fit_results.find(
                  (f) => f.role_id === roleId && f.department_id === deptId,
                );
                setSelectedFit(fit || null);
              }}
              disabled={!personDetail}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-200 disabled:opacity-50 focus:outline-none focus:border-emerald-500/50"
            >
              <option value="">선택하세요</option>
              {(personDetail?.fit_results || []).map((f) => (
                <option
                  key={`${f.role_id}|${f.department_id}`}
                  value={`${f.role_id}|${f.department_id}`}
                >
                  {f.role_title} ({f.department_name}) — Fit{" "}
                  {(f.fit_score * 100).toFixed(0)}%
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Breakdown display */}
      {breakdownLoading && (
        <div className="text-zinc-500 text-sm text-center py-8">
          계산 중...
        </div>
      )}

      {breakdown && (
        <div className="space-y-4">
          {/* Summary card */}
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-semibold text-zinc-200">
                  {breakdown.person_name} → {breakdown.role_title}
                </h3>
                <p className="text-xs text-zinc-500">
                  {breakdown.department_name}
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-emerald-400">
                  {(breakdown.final_fit_score * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-zinc-500">
                  예측 성과: {breakdown.final_predicted_performance}/5.0
                </div>
              </div>
            </div>
            <p className="text-sm text-zinc-400">{breakdown.summary_ko}</p>
          </div>

          {/* Step-by-step breakdown */}
          {breakdown.steps.map((step) => (
            <StepCard key={step.step_number} step={step} />
          ))}

          {/* Final calculation */}
          <div className="bg-zinc-900 rounded-xl border border-emerald-500/30 p-4">
            <h4 className="text-sm font-semibold text-emerald-400 mb-2">
              최종 계산
            </h4>
            <div className="space-y-1 font-mono text-xs">
              {breakdown.steps.map((s) => (
                <div key={s.step_number} className="flex justify-between">
                  <span className="text-zinc-400">
                    {s.component_ko} ({s.weight > 0 ? `${(s.weight * 100).toFixed(0)}%` : `−${(Math.abs(s.weight) * 100).toFixed(0)}%`})
                  </span>
                  <span
                    className={
                      s.weighted_value >= 0
                        ? "text-emerald-400"
                        : "text-red-400"
                    }
                  >
                    {s.weighted_value >= 0 ? "+" : ""}
                    {s.weighted_value.toFixed(4)}
                  </span>
                </div>
              ))}
              <div className="flex justify-between pt-2 border-t border-zinc-700 text-sm font-semibold">
                <span className="text-zinc-200">FitScore</span>
                <span className="text-emerald-400">
                  {breakdown.final_fit_score.toFixed(4)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!breakdown && !breakdownLoading && selectedFit && (
        <div className="text-zinc-500 text-sm text-center py-8">
          분해 결과를 불러올 수 없습니다.
        </div>
      )}
    </div>
  );
}

function StepCard({ step }: { step: ScoreStep }) {
  const [isOpen, setIsOpen] = useState(false);

  const componentColors: Record<string, string> = {
    skill_match: "border-emerald-500/30",
    historical_performance: "border-amber-500/30",
    level_match: "border-violet-500/30",
    burnout_risk: "border-red-500/30",
  };

  const borderColor = componentColors[step.component] || "border-zinc-700";

  return (
    <div
      className={`bg-zinc-900 rounded-xl border ${borderColor} overflow-hidden`}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full text-left p-4 hover:bg-zinc-800/30 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono text-zinc-600 w-6">
              #{step.step_number}
            </span>
            <div>
              <span className="text-sm font-medium text-zinc-200">
                {step.component_ko}
              </span>
              <span className="text-xs text-zinc-500 ml-2">
                {step.component}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm font-mono text-zinc-200">
                {step.intermediate_value.toFixed(4)}
              </div>
              <div
                className={`text-xs font-mono ${
                  step.weighted_value >= 0 ? "text-emerald-400" : "text-red-400"
                }`}
              >
                → {step.weighted_value >= 0 ? "+" : ""}
                {step.weighted_value.toFixed(4)}
              </div>
            </div>
            <ChevronDown
              size={14}
              className={`text-zinc-500 transition-transform ${
                isOpen ? "rotate-180" : ""
              }`}
            />
          </div>
        </div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-3 border-t border-zinc-800 pt-3">
              <div>
                <span className="text-xs text-zinc-500">적용 공식:</span>
                <code className="block text-xs text-emerald-300 font-mono mt-1 bg-zinc-800 p-2 rounded">
                  {step.formula_applied}
                </code>
              </div>

              <p className="text-sm text-zinc-400">{step.explanation_ko}</p>
              <p className="text-xs text-zinc-600">{step.explanation_en}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
