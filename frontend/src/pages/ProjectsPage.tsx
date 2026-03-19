import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import {
  Plus,
  FolderKanban,
  Users,
  CheckCircle,
  XCircle,
  AlertCircle,
  Star,
  Upload,
} from "lucide-react";
import { api } from "../api";
import type {
  Project,
  ProjectDetail,
  PersonSummary,
} from "../types";
import { DifficultyBadge } from "../components/estimation/DifficultyBadge";
import { ScoutReport } from "../components/estimation/ScoutReport";

const STATUS_STYLE: Record<string, string> = {
  planned: "bg-blue-900/50 text-blue-400",
  in_progress: "bg-amber-900/50 text-amber-400",
  completed: "bg-emerald-900/50 text-emerald-400",
  cancelled: "bg-zinc-800 text-zinc-500",
};

const RESULT_CONFIG = [
  { label: "", icon: null },
  { label: "Failure", icon: XCircle, color: "text-red-400" },
  { label: "Partial", icon: AlertCircle, color: "text-amber-400" },
  { label: "Success", icon: CheckCircle, color: "text-emerald-400" },
  { label: "Excellent", icon: Star, color: "text-yellow-400" },
];

export function ProjectsPage() {
  const { t } = useTranslation();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ProjectDetail | null>(null);
  const [people, setPeople] = useState<PersonSummary[]>([]);
  const [skills, setSkills] = useState<{ id: string; name: string }[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [showScout, setShowScout] = useState<{ id: string; name: string } | null>(null);
  const [tab, setTab] = useState<"projects" | "import">("projects");

  // Form state
  const [formName, setFormName] = useState("");
  const [formDifficulty, setFormDifficulty] = useState(3);
  const [formSkills, setFormSkills] = useState<string[]>([]);

  useEffect(() => {
    loadProjects();
    api.getPeople().then(setPeople).catch(() => {});
    fetch("/api/estimation/skills")
      .then((r) => { if (!r.ok) throw new Error(); return r.json(); })
      .then((s) => { if (Array.isArray(s)) setSkills(s); })
      .catch(() => {});
  }, []);

  const loadProjects = () => {
    api.getProjects().then(setProjects).catch(() => {});
  };

  const loadDetail = (id: string) => {
    setSelectedId(id);
    api.getProject(id).then(setDetail).catch(() => {});
  };

  const handleCreate = async () => {
    if (!formName) return;
    try {
      const res = await api.createProject({
        name: formName,
        difficulty: formDifficulty,
        required_skill_ids: formSkills,
      });
      setShowCreate(false);
      setFormName("");
      setFormDifficulty(3);
      setFormSkills([]);
      loadProjects();
      loadDetail(res.id);
    } catch {}
  };

  const handleAssign = async (personId: string) => {
    if (!selectedId) return;
    await api.assignToProject(selectedId, personId, "contributor");
    loadDetail(selectedId);
  };

  const handleOutcome = async (personId: string, result: number) => {
    if (!selectedId) return;
    await api.recordOutcome(selectedId, personId, result);
    loadDetail(selectedId);
    loadProjects();
  };

  // CSV import
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [importResult, setImportResult] = useState<{
    imported_count: number;
    errors: string[];
    warnings: string[];
  } | null>(null);

  const handleImport = async () => {
    if (!csvFile) return;
    try {
      const result = await api.importCsv(csvFile);
      setImportResult(result);
    } catch (e) {
      setImportResult({ imported_count: 0, errors: [String(e)], warnings: [] });
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">
            {t("projects.title")}
          </h1>
          <p className="text-xs text-zinc-500">{t("projects.subtitle")}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setTab("projects")}
            className={`px-3 py-1.5 rounded-lg text-xs ${
              tab === "projects"
                ? "bg-emerald-600 text-white"
                : "bg-zinc-800 text-zinc-400"
            }`}
          >
            <FolderKanban size={12} className="inline mr-1" />
            {t("projects.projects")}
          </button>
          <button
            onClick={() => setTab("import")}
            className={`px-3 py-1.5 rounded-lg text-xs ${
              tab === "import"
                ? "bg-emerald-600 text-white"
                : "bg-zinc-800 text-zinc-400"
            }`}
          >
            <Upload size={12} className="inline mr-1" />
            {t("import.title")}
          </button>
        </div>
      </div>

      {tab === "import" && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-zinc-200">
            {t("import.title")}
          </h2>
          <p className="text-xs text-zinc-500">{t("import.description")}</p>

          {/* CSV format example */}
          <div className="bg-zinc-800 rounded-lg p-3 font-mono text-xs text-zinc-400">
            <p className="text-zinc-500 mb-1"># CSV format:</p>
            <p>이름,직급,부서,입사일</p>
            <p>김철수,과장,영업부,2020-03-15</p>
            <p>이영희,사원,개발부,2023-01-01</p>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
              className="text-xs text-zinc-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-zinc-800 file:text-zinc-300 file:text-xs file:cursor-pointer"
            />
            <button
              onClick={handleImport}
              disabled={!csvFile}
              className="px-4 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-medium hover:bg-emerald-500 disabled:opacity-30 transition-colors"
            >
              {t("import.confirm")}
            </button>
          </div>

          {importResult && (
            <div className="space-y-2">
              <p className="text-sm text-emerald-400">
                {importResult.imported_count}명 가져옴
              </p>
              {importResult.errors.map((e, i) => (
                <p key={i} className="text-xs text-red-400">
                  {e}
                </p>
              ))}
              {importResult.warnings.map((w, i) => (
                <p key={i} className="text-xs text-amber-400">
                  {w}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "projects" && (
        <div className="flex gap-4" style={{ height: "calc(100vh - 10rem)" }}>
          {/* Left: Project List */}
          <div className="w-80 flex flex-col gap-3 shrink-0">
            <button
              onClick={() => setShowCreate(true)}
              className="w-full px-3 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors flex items-center justify-center gap-1"
            >
              <Plus size={14} />
              {t("projects.create")}
            </button>

            <div className="flex-1 overflow-y-auto space-y-2">
              {projects.map((p) => (
                <button
                  key={p.id}
                  onClick={() => loadDetail(p.id)}
                  className={`w-full text-left p-3 rounded-xl border transition-all ${
                    selectedId === p.id
                      ? "border-emerald-500 bg-emerald-500/10"
                      : "border-zinc-800 bg-zinc-900 hover:border-zinc-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-zinc-200 truncate">
                      {p.name}
                    </span>
                    <DifficultyBadge level={p.difficulty} />
                  </div>
                  <div className="flex items-center gap-2 text-[10px]">
                    <span className={`px-1.5 py-0.5 rounded ${STATUS_STYLE[p.status] || ""}`}>
                      {p.status}
                    </span>
                    <span className="text-zinc-500">
                      <Users size={10} className="inline mr-0.5" />
                      {p.assignment_count || 0}
                    </span>
                  </div>
                </button>
              ))}
              {projects.length === 0 && (
                <p className="text-center text-xs text-zinc-600 py-8">
                  {t("projects.empty")}
                </p>
              )}
            </div>
          </div>

          {/* Right: Detail */}
          <div className="flex-1 overflow-y-auto">
            {detail ? (
              <div className="space-y-4">
                {/* Project info */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-zinc-200">
                      {detail.name}
                    </h2>
                    <DifficultyBadge level={detail.difficulty} />
                  </div>
                  {detail.description && (
                    <p className="text-xs text-zinc-500">{detail.description}</p>
                  )}
                  <div className="flex gap-3 text-xs text-zinc-500">
                    <span>{t("projects.start")}: {detail.start_date}</span>
                    {detail.end_date && (
                      <span>{t("projects.end")}: {detail.end_date}</span>
                    )}
                  </div>
                  {detail.required_skills.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {detail.required_skills.map((s) => (
                        <span
                          key={s.id}
                          className="px-2 py-0.5 rounded bg-zinc-800 text-xs text-zinc-400"
                        >
                          {s.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Assignments */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium text-zinc-300">
                      {t("projects.assignedPeople")}
                    </h3>
                  </div>

                  {detail.assignments.map((a) => {
                    const hasOutcome = detail.outcomes.some(
                      (o) => o.person_id === a.person_id,
                    );
                    const outcome = detail.outcomes.find(
                      (o) => o.person_id === a.person_id,
                    );
                    return (
                      <div
                        key={a.id}
                        className="flex items-center justify-between py-2 border-b border-zinc-800/50 last:border-0"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-zinc-200">
                            {a.person_name}
                          </span>
                          <span className="text-[10px] text-zinc-500 px-1 bg-zinc-800 rounded">
                            {a.role}
                          </span>
                          {outcome && (
                            <span className={`text-xs ${RESULT_CONFIG[outcome.result]?.color}`}>
                              {RESULT_CONFIG[outcome.result]?.label}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-1">
                          {!hasOutcome &&
                            [1, 2, 3, 4].map((r) => {
                              const cfg = RESULT_CONFIG[r];
                              const Icon = cfg.icon!;
                              return (
                                <button
                                  key={r}
                                  onClick={() => handleOutcome(a.person_id, r)}
                                  title={cfg.label}
                                  className={`p-1 rounded hover:bg-zinc-800 ${cfg.color}`}
                                >
                                  <Icon size={14} />
                                </button>
                              );
                            })}
                          <button
                            onClick={() =>
                              setShowScout({
                                id: a.person_id,
                                name: a.person_name,
                              })
                            }
                            className="p-1 rounded hover:bg-zinc-800 text-zinc-500 hover:text-emerald-400 ml-1"
                            title={t("scout.title")}
                          >
                            <Users size={14} />
                          </button>
                        </div>
                      </div>
                    );
                  })}

                  {/* Add person */}
                  <div className="pt-2">
                    <select
                      onChange={(e) => {
                        if (e.target.value) handleAssign(e.target.value);
                        e.target.value = "";
                      }}
                      className="w-full bg-zinc-800 border border-zinc-700 rounded-lg text-xs text-zinc-300 px-2 py-1.5"
                      defaultValue=""
                    >
                      <option value="" disabled>
                        + {t("projects.addPerson")}
                      </option>
                      {people
                        .filter(
                          (p) =>
                            !detail.assignments.some(
                              (a) => a.person_id === p.id,
                            ),
                        )
                        .map((p) => (
                          <option key={p.id} value={p.id}>
                            {p.name} ({p.active_role || "—"})
                          </option>
                        ))}
                    </select>
                  </div>
                </div>

                {/* Scout Report (if selected) */}
                {showScout && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-zinc-900 border border-zinc-800 rounded-xl p-4"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-medium text-zinc-300">
                        {showScout.name} — {t("scout.title")}
                      </h3>
                      <button
                        onClick={() => setShowScout(null)}
                        className="text-xs text-zinc-500 hover:text-zinc-300"
                      >
                        {t("common.cancel")}
                      </button>
                    </div>
                    <ScoutReport
                      personId={showScout.id}
                      personName={showScout.name}
                    />
                  </motion.div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-zinc-600 text-sm">
                {t("projects.selectProject")}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showCreate && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
          onClick={() => setShowCreate(false)}
        >
          <div
            className="bg-zinc-900 border border-zinc-700 rounded-2xl w-full max-w-md p-5 space-y-4 mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-lg font-semibold text-zinc-200">
              {t("projects.create")}
            </h2>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-zinc-500 block mb-1">
                  {t("projects.projectName")}
                </label>
                <input
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="e.g. API Migration"
                  className="w-full bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-lg px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="text-xs text-zinc-500 block mb-1">
                  {t("projects.difficulty")} ({formDifficulty})
                </label>
                <input
                  type="range"
                  min={1}
                  max={5}
                  value={formDifficulty}
                  onChange={(e) => setFormDifficulty(parseInt(e.target.value))}
                  className="w-full accent-emerald-500"
                />
                <div className="flex justify-between text-[10px] text-zinc-600">
                  <span>Trivial</span>
                  <span>Easy</span>
                  <span>Moderate</span>
                  <span>Hard</span>
                  <span>Extreme</span>
                </div>
              </div>

              <div>
                <label className="text-xs text-zinc-500 block mb-1">
                  {t("projects.requiredSkills")}
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {skills.map((s) => (
                    <button
                      key={s.id}
                      onClick={() =>
                        setFormSkills((prev) =>
                          prev.includes(s.id)
                            ? prev.filter((id) => id !== s.id)
                            : [...prev, s.id],
                        )
                      }
                      className={`px-2 py-1 rounded text-xs ${
                        formSkills.includes(s.id)
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : "bg-zinc-800 text-zinc-400 border border-zinc-700"
                      }`}
                    >
                      {s.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 rounded-lg bg-zinc-800 text-zinc-300 text-sm"
              >
                {t("common.cancel")}
              </button>
              <button
                onClick={handleCreate}
                disabled={!formName}
                className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 disabled:opacity-30 transition-colors"
              >
                {t("projects.create")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
