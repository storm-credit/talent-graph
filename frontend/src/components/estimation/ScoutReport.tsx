import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import { Radar, Shield, Zap } from "lucide-react";
import { api } from "../../api";
import type { ScoutReport as ScoutReportType } from "../../types";
import { SkillEstimateBar } from "./SkillEstimateBar";

interface Props {
  personId: string;
  personName: string;
}

export function ScoutReport({ personId, personName }: Props) {
  const { t } = useTranslation();
  const [report, setReport] = useState<ScoutReportType | null>(null);
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    setLoading(true);
    api
      .getScoutReport(personId)
      .then((r) => {
        setReport(r);
        setInitialized(r.estimates.length > 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [personId]);

  const handleInitialize = async () => {
    setLoading(true);
    try {
      await api.initializeEstimates();
      const r = await api.getScoutReport(personId);
      setReport(r);
      setInitialized(true);
    } catch {}
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8 text-zinc-500 text-sm">
        {t("common.loading")}
      </div>
    );
  }

  if (!initialized || !report || report.estimates.length === 0) {
    return (
      <div className="text-center py-8 space-y-3">
        <Radar size={32} className="mx-auto text-zinc-600" />
        <p className="text-sm text-zinc-500">{t("scout.noData")}</p>
        <button
          onClick={handleInitialize}
          className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors"
        >
          {t("scout.initialize")}
        </button>
      </div>
    );
  }

  const confColor =
    report.avg_confidence > 70
      ? "text-emerald-400"
      : report.avg_confidence > 40
        ? "text-amber-400"
        : "text-zinc-500";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield size={16} className="text-emerald-400" />
          <span className="text-sm font-medium text-zinc-200">
            {t("scout.title")}
          </span>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className={confColor}>
            {t("scout.confidence")}: {report.avg_confidence.toFixed(0)}%
          </span>
          <span className="text-zinc-500">
            <Zap size={10} className="inline mr-0.5" />
            {report.total_projects} {t("scout.projectsEvaluated")}
          </span>
        </div>
      </div>

      {/* Skill bars */}
      <div className="space-y-3">
        {report.estimates
          .sort((a, b) => b.mu - a.mu)
          .map((est) => (
            <SkillEstimateBar key={est.skill_id} est={est} />
          ))}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-[10px] text-zinc-600 pt-2 border-t border-zinc-800">
        <span>
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 mr-1" />
          {t("scout.highConf")}
        </span>
        <span>
          <span className="inline-block w-2 h-2 rounded-full bg-amber-500 mr-1" />
          {t("scout.medConf")}
        </span>
        <span>
          <span className="inline-block w-2 h-2 rounded-full bg-zinc-500 mr-1" />
          {t("scout.lowConf")}
        </span>
        <span className="ml-auto">
          Bayesian estimation (Normal-Normal conjugate)
        </span>
      </div>
    </motion.div>
  );
}
