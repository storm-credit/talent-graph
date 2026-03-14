import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { X } from "lucide-react";
import { useGameModeStore } from "../../store/gameMode";

function scoreColor(score: number): string {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-amber-400";
  if (score >= 40) return "text-orange-400";
  return "text-red-400";
}

export function QuarterSummaryPanel() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const { advanceResult, processedChanges, dismissSummary } = useGameModeStore();

  if (!advanceResult) return null;
  const report = advanceResult.report;
  const cs = report.company_score;

  const growthCount = processedChanges.filter((c) => c.change_type === "skill_growth").length;
  const departureCount = processedChanges.filter((c) => c.change_type === "departure").length;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
      onClick={dismissSummary}
    >
      <motion.div
        initial={{ scale: 0.9, y: 30, opacity: 0 }}
        animate={{ scale: 1, y: 0, opacity: 1 }}
        exit={{ scale: 0.9, y: 30, opacity: 0 }}
        transition={{ type: "spring", damping: 22, stiffness: 200 }}
        className="bg-zinc-900 border border-zinc-700 rounded-2xl w-full max-w-md max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 border-b border-zinc-800 flex items-center justify-between">
          <div>
            <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
              {t("report.quarterReport")}
            </p>
            <p className="text-xl font-bold text-zinc-100">{report.quarter}</p>
          </div>
          <button
            onClick={dismissSummary}
            className="p-1 text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Company Score */}
        <div className="p-5 text-center border-b border-zinc-800">
          <p className="text-xs text-zinc-500">{t("report.companyScore")}</p>
          <p className={`text-4xl font-bold ${scoreColor(cs.total)}`}>
            {cs.total}
          </p>
          {report.score_delta !== null && (
            <p
              className={`text-sm mt-0.5 ${report.score_delta >= 0 ? "text-emerald-400" : "text-red-400"}`}
            >
              {report.score_delta >= 0 ? "+" : ""}
              {report.score_delta}
            </p>
          )}

          {/* Breakdown */}
          <div className="grid grid-cols-5 gap-1 mt-3 text-[10px]">
            {[
              { label: t("report.teamPerf"), val: cs.team_performance },
              { label: t("report.morale"), val: cs.morale_health },
              { label: t("report.retention"), val: cs.retention_rate },
              { label: t("report.skillCov"), val: cs.skill_coverage },
              { label: t("report.growth"), val: cs.growth_rate },
            ].map(({ label, val }) => (
              <div key={label}>
                <p className="text-zinc-500">{label}</p>
                <p className={`font-mono font-bold ${scoreColor(val)}`}>{val}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Headlines */}
        {report.headlines.length > 0 && (
          <div className="px-5 py-3 border-b border-zinc-800">
            <p className="text-xs text-zinc-500 mb-2">{t("report.headlines")}</p>
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
            <p className="text-xs text-zinc-500 mb-0.5">MVP</p>
            <p className="text-sm text-amber-400 font-medium">
              🏆 {lang === "ko" ? report.mvp.description_ko : report.mvp.description}
            </p>
          </div>
        )}

        {/* Warnings */}
        {report.warnings.length > 0 && (
          <div className="px-5 py-3 border-b border-zinc-800">
            <p className="text-xs text-zinc-500 mb-0.5">{t("report.warnings")}</p>
            {report.warnings.map((w, i) => (
              <p key={i} className="text-xs text-red-400">
                ⚠️ {lang === "ko" ? w.description_ko : w.description}
              </p>
            ))}
          </div>
        )}

        {/* Stats */}
        <div className="px-5 py-3 border-b border-zinc-800">
          <div className="grid grid-cols-4 gap-3 text-center text-xs">
            <div className="bg-zinc-800/50 rounded-lg p-2">
              <p className="text-zinc-500 text-[10px]">{t("report.active")}</p>
              <p className="font-bold text-zinc-200">{report.total_active}</p>
            </div>
            <div className="bg-zinc-800/50 rounded-lg p-2">
              <p className="text-zinc-500 text-[10px]">{t("report.avgMorale")}</p>
              <p className="font-bold text-zinc-200">
                {(report.avg_morale * 100).toFixed(0)}%
              </p>
            </div>
            <div className="bg-zinc-800/50 rounded-lg p-2">
              <p className="text-zinc-500 text-[10px]">{t("report.growthLabel")}</p>
              <p className="font-bold text-emerald-400">+{growthCount}</p>
            </div>
            <div className="bg-zinc-800/50 rounded-lg p-2">
              <p className="text-zinc-500 text-[10px]">{t("report.departures")}</p>
              <p className="font-bold text-red-400">{departureCount}</p>
            </div>
          </div>
        </div>

        {/* Milestones */}
        {advanceResult.newly_unlocked.length > 0 && (
          <div className="px-5 py-3 border-b border-zinc-800">
            <p className="text-xs text-amber-400 mb-2">
              🎉 {t("report.newMilestones")}
            </p>
            {advanceResult.newly_unlocked.map((a) => (
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

        {/* Continue button */}
        <div className="p-4">
          <button
            onClick={dismissSummary}
            className="w-full py-2.5 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors"
          >
            {t("report.continue")}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
