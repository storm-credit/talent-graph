import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSimulationStore } from "../store/simulation";
import type { ChangeRecord } from "../types";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, SkipBack, X } from "lucide-react";
import { ratingColor } from "../lib/utils";

function changeIcon(type: string) {
  switch (type) {
    case "outcome":
      return "bg-emerald-500";
    case "burnout_change":
      return "bg-amber-500";
    case "morale_change":
      return "bg-blue-500";
    case "skill_growth":
      return "bg-cyan-500";
    case "skill_decay":
      return "bg-orange-500";
    case "departure":
      return "bg-red-500";
    case "event":
      return "bg-purple-500";
    case "certification":
      return "bg-cyan-400";
    case "mentoring":
      return "bg-indigo-500";
    case "personal_event":
      return "bg-yellow-500";
    default:
      return "bg-zinc-500";
  }
}

function changeLabel(type: string) {
  switch (type) {
    case "outcome":
      return "Outcome";
    case "burnout_change":
      return "Burnout";
    case "morale_change":
      return "Morale";
    case "skill_growth":
      return "Growth";
    case "skill_decay":
      return "Decay";
    case "departure":
      return "Departed";
    case "event":
      return "Event";
    case "certification":
      return "Cert";
    case "mentoring":
      return "Mentor";
    case "personal_event":
      return "Personal";
    default:
      return type;
  }
}

function scoreColor(score: number): string {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-amber-400";
  if (score >= 40) return "text-orange-400";
  return "text-red-400";
}

export function SimulationPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;

  const {
    status,
    lastAdvance,
    allChanges,
    loading,
    showReport,
    fetchStatus,
    advance,
    rollback,
    reset,
    closeReport,
    fetchAnalyticsData,
  } = useSimulationStore();
  const [animatingChanges, setAnimatingChanges] = useState<ChangeRecord[]>([]);

  useEffect(() => {
    fetchStatus();
    fetchAnalyticsData();
  }, []);

  const handleAdvance = async () => {
    try {
      const result = await advance();
      // Stagger animation for changes feed
      setAnimatingChanges([]);
      for (let i = 0; i < result.changes.length; i++) {
        setTimeout(() => {
          setAnimatingChanges((prev) => [...prev, result.changes[i]]);
        }, i * 80);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const report = lastAdvance?.report;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">
            {t("simulation.title")}
          </h1>
          <p className="text-sm text-zinc-500">
            {status
              ? `${t("simulation.currentQuarter")} ${status.current_quarter} · ${status.history_length} ${t("simulation.historyLength")}`
              : t("common.loading")}
            {status?.enhanced_mode && (
              <span className="ml-2 text-emerald-500">
                ● {t("simulation.enhanced")}
              </span>
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => rollback(1)}
            disabled={loading || !status || status.history_length === 0}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-zinc-800 text-zinc-300 text-sm hover:bg-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <SkipBack size={14} />
            {t("simulation.rollback")}
          </button>
          <button
            onClick={reset}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-zinc-800 text-zinc-300 text-sm hover:bg-zinc-700 disabled:opacity-30 transition-colors"
          >
            <RotateCcw size={14} />
            {t("simulation.reset")}
          </button>
          <button
            onClick={handleAdvance}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 disabled:opacity-50 transition-colors"
          >
            <Play size={14} />
            {loading ? t("common.loading") : t("simulation.advanceQuarter")}
          </button>
        </div>
      </div>

      {/* Stats bar */}
      {status && (
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
            <p className="text-xs text-zinc-500">
              {t("simulation.activePeople")}
            </p>
            <p className="text-lg font-bold text-zinc-100">
              {status.active_people}
            </p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
            <p className="text-xs text-zinc-500">
              {t("simulation.departed")}
            </p>
            <p className="text-lg font-bold text-red-400">
              {status.departed_people}
            </p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
            <p className="text-xs text-zinc-500">
              {t("simulation.avgMorale")}
            </p>
            <p
              className={`text-lg font-bold ${status.average_morale >= 0.7 ? "text-emerald-400" : status.average_morale >= 0.4 ? "text-amber-400" : "text-red-400"}`}
            >
              {(status.average_morale * 100).toFixed(0)}%
            </p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
            <p className="text-xs text-zinc-500">
              {t("simulation.currentQuarter")}
            </p>
            <p className="text-lg font-bold text-zinc-100">
              {status.history_length}
            </p>
          </div>
        </div>
      )}

      {/* Timeline */}
      {status && status.history_length > 0 && (
        <div className="flex items-center gap-1 overflow-x-auto pb-2">
          {Array.from({ length: status.history_length }, (_, i) => {
            const year = 2025 + Math.floor(i / 4);
            const q = (i % 4) + 1;
            return (
              <div
                key={i}
                className="flex-shrink-0 px-3 py-1.5 rounded-md bg-emerald-500/15 border border-emerald-500/20 text-xs font-mono text-emerald-400"
              >
                {year}-Q{q}
              </div>
            );
          })}
          <div className="flex-shrink-0 px-3 py-1.5 rounded-md bg-zinc-800 border border-zinc-700 text-xs font-mono text-zinc-300">
            {status.current_quarter} ←
          </div>
        </div>
      )}

      {/* Changes Feed */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl">
        <div className="px-4 py-3 border-b border-zinc-800">
          <h2 className="text-sm font-semibold text-zinc-300">
            {lastAdvance
              ? `${t("simulation.changes")} — ${lastAdvance.quarter} (${animatingChanges.length})`
              : t("simulation.noChanges")}
          </h2>
        </div>
        <div className="divide-y divide-zinc-800/50 max-h-[500px] overflow-y-auto">
          <AnimatePresence>
            {animatingChanges.map((change, i) => (
              <motion.div
                key={`${change.person_id}-${change.change_type}-${i}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className="px-4 py-3 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-2 h-2 rounded-full ${changeIcon(change.change_type)}`}
                  />
                  <div>
                    <p className="text-sm text-zinc-200">
                      {change.person_name}
                    </p>
                    <p className="text-xs text-zinc-500">
                      {change.description}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 capitalize">
                    {changeLabel(change.change_type)}
                  </span>
                  {change.change_type === "outcome" && change.rating && (
                    <span
                      className={`text-xs font-mono font-semibold capitalize ${ratingColor(change.rating)}`}
                    >
                      {change.rating}
                    </span>
                  )}
                  {(change.change_type === "burnout_change" ||
                    change.change_type === "morale_change") && (
                    <div className="text-xs font-mono text-amber-400">
                      {change.old_value} → {change.new_value}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {animatingChanges.length === 0 && !lastAdvance && (
            <div className="px-4 py-8 text-center text-zinc-600 text-sm">
              {t("simulation.noChanges")}
            </div>
          )}
        </div>
      </div>

      {/* Full History */}
      {allChanges.length > 0 && lastAdvance && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl">
          <div className="px-4 py-3 border-b border-zinc-800">
            <h2 className="text-sm font-semibold text-zinc-300">
              {t("simulation.historyLength")} ({allChanges.length})
            </h2>
          </div>
          <div className="divide-y divide-zinc-800/50 max-h-[300px] overflow-y-auto">
            {allChanges
              .slice()
              .reverse()
              .slice(0, 50)
              .map((c, i) => (
                <div
                  key={i}
                  className="px-4 py-2 text-xs text-zinc-400 flex justify-between"
                >
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-1.5 h-1.5 rounded-full ${changeIcon(c.change_type)}`}
                    />
                    <span>{c.description}</span>
                  </div>
                  {c.rating && (
                    <span
                      className={`font-mono capitalize ${ratingColor(c.rating)}`}
                    >
                      {c.rating}
                    </span>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}

      {/* ── Quarter Report Modal ── */}
      <AnimatePresence>
        {showReport && report && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
            onClick={closeReport}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: "spring", damping: 20 }}
              className="bg-zinc-900 border border-zinc-700 rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="p-5 border-b border-zinc-800 text-center relative">
                <button
                  onClick={closeReport}
                  className="absolute right-4 top-4 text-zinc-500 hover:text-zinc-300"
                >
                  <X size={16} />
                </button>
                <p className="text-xs text-zinc-500 uppercase tracking-wider">
                  {t("report.quarterReport")}
                </p>
                <h2 className="text-xl font-bold text-zinc-100 mt-1">
                  {report.quarter}
                </h2>
              </div>

              {/* Company Score */}
              <div className="px-5 py-4 text-center border-b border-zinc-800">
                <p className="text-xs text-zinc-500 mb-1">
                  {t("report.companyScore")}
                </p>
                <p
                  className={`text-4xl font-bold ${scoreColor(report.company_score.total)}`}
                >
                  {report.company_score.total}
                </p>
                {report.score_delta !== null && (
                  <p
                    className={`text-sm mt-1 ${report.score_delta >= 0 ? "text-emerald-400" : "text-red-400"}`}
                  >
                    {report.score_delta >= 0 ? "+" : ""}
                    {report.score_delta}
                  </p>
                )}
                {/* Score breakdown */}
                <div className="grid grid-cols-5 gap-1 mt-3 text-[10px]">
                  {[
                    {
                      label: t("report.teamPerf"),
                      val: report.company_score.team_performance,
                    },
                    {
                      label: t("report.morale"),
                      val: report.company_score.morale_health,
                    },
                    {
                      label: t("report.retention"),
                      val: report.company_score.retention_rate,
                    },
                    {
                      label: t("report.skillCov"),
                      val: report.company_score.skill_coverage,
                    },
                    {
                      label: t("report.growth"),
                      val: report.company_score.growth_rate,
                    },
                  ].map(({ label, val }) => (
                    <div key={label}>
                      <p className="text-zinc-500">{label}</p>
                      <p className={`font-mono ${scoreColor(val)}`}>{val}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Headlines */}
              {report.headlines.length > 0 && (
                <div className="px-5 py-3 border-b border-zinc-800">
                  <p className="text-xs text-zinc-500 mb-2">
                    {t("report.headlines")}
                  </p>
                  <div className="space-y-1.5">
                    {report.headlines.slice(0, 5).map((h, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className={`flex items-center gap-2 text-xs ${
                          h.category === "positive"
                            ? "text-emerald-400"
                            : h.category === "negative"
                              ? "text-red-400"
                              : "text-zinc-400"
                        }`}
                      >
                        <span>{h.icon}</span>
                        <span>{lang === "ko" ? h.text_ko : h.text}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}

              {/* MVP */}
              {report.mvp && (
                <div className="px-5 py-3 border-b border-zinc-800">
                  <p className="text-xs text-zinc-500 mb-1">🏆 MVP</p>
                  <p className="text-sm text-amber-400 font-medium">
                    {lang === "ko"
                      ? report.mvp.description_ko
                      : report.mvp.description}
                  </p>
                </div>
              )}

              {/* Warnings */}
              {report.warnings.length > 0 && (
                <div className="px-5 py-3 border-b border-zinc-800">
                  <p className="text-xs text-zinc-500 mb-1">
                    ⚠️ {t("report.warnings")}
                  </p>
                  {report.warnings.map((w, i) => (
                    <p key={i} className="text-xs text-red-400">
                      {lang === "ko" ? w.description_ko : w.description}
                    </p>
                  ))}
                </div>
              )}

              {/* Stats */}
              <div className="px-5 py-3 border-b border-zinc-800">
                <div className="grid grid-cols-4 gap-3 text-center text-xs">
                  <div>
                    <p className="text-zinc-500">{t("report.active")}</p>
                    <p className="font-bold text-zinc-200">
                      {report.total_active}
                    </p>
                  </div>
                  <div>
                    <p className="text-zinc-500">{t("report.avgMorale")}</p>
                    <p className="font-bold text-zinc-200">
                      {(report.avg_morale * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-zinc-500">{t("report.growthLabel")}</p>
                    <p className="font-bold text-emerald-400">
                      +{report.growth_events}
                    </p>
                  </div>
                  <div>
                    <p className="text-zinc-500">{t("report.departures")}</p>
                    <p className="font-bold text-red-400">
                      {report.departures_this_quarter}
                    </p>
                  </div>
                </div>
              </div>

              {/* Newly Unlocked Milestones */}
              {lastAdvance && lastAdvance.newly_unlocked.length > 0 && (
                <div className="px-5 py-3 border-b border-zinc-800">
                  <p className="text-xs text-amber-400 mb-2">
                    🎉 {t("report.newMilestones")}
                  </p>
                  {lastAdvance.newly_unlocked.map((a) => (
                    <motion.div
                      key={a.id}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="flex items-center gap-2 p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 mb-1"
                    >
                      <span className="text-lg">{a.icon}</span>
                      <div>
                        <p className="text-xs font-medium text-amber-400">
                          {lang === "ko" ? a.name_ko : a.name}
                        </p>
                        <p className="text-[10px] text-zinc-500">
                          {lang === "ko" ? a.description_ko : a.description}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}

              {/* Continue Button */}
              <div className="p-4">
                <button
                  onClick={closeReport}
                  className="w-full py-2.5 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors"
                >
                  {t("report.continue")}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
