import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import type { CompanyOverview, PersonSummary } from "../types";
import { MetricCard } from "../components/MetricCard";
import { BurnoutBadge } from "../components/BurnoutBadge";
import { burnoutColor } from "../lib/utils";
import { useSimulationStore } from "../store/simulation";
import { TrendingUp, Award } from "lucide-react";

function moraleColor(morale: number): string {
  if (morale >= 0.7) return "text-emerald-400";
  if (morale >= 0.4) return "text-amber-400";
  return "text-red-400";
}

function moraleBg(morale: number): string {
  if (morale >= 0.7) return "bg-emerald-500";
  if (morale >= 0.4) return "bg-amber-500";
  return "bg-red-500";
}

function scoreColor(score: number): string {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-amber-400";
  if (score >= 40) return "text-orange-400";
  return "text-red-400";
}

function scoreBg(score: number): string {
  if (score >= 80) return "bg-emerald-500";
  if (score >= 60) return "bg-amber-500";
  if (score >= 40) return "bg-orange-500";
  return "bg-red-500";
}

export function DashboardPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const [company, setCompany] = useState<CompanyOverview | null>(null);
  const [people, setPeople] = useState<PersonSummary[]>([]);
  const status = useSimulationStore((s) => s.status);
  const fetchStatus = useSimulationStore((s) => s.fetchStatus);
  const scoreHistory = useSimulationStore((s) => s.scoreHistory);
  const achievements = useSimulationStore((s) => s.achievements);
  const achievementProgress = useSimulationStore(
    (s) => s.achievementProgress,
  );
  const fetchAnalyticsData = useSimulationStore((s) => s.fetchAnalyticsData);

  useEffect(() => {
    api.getCompany().then(setCompany);
    api.getPeople().then(setPeople);
    fetchStatus();
    fetchAnalyticsData();
  }, []);

  if (!company)
    return <div className="text-zinc-500">{t("common.loading")}</div>;

  const activePeople = people.filter((p) => !p.departed);
  const departedPeople = people.filter((p) => p.departed);
  const burnoutWarnings = activePeople.filter((p) => p.burnout_risk > 0.3);
  const lowMorale = activePeople.filter((p) => p.morale < 0.4);
  const avgMorale =
    activePeople.length > 0
      ? activePeople.reduce((s, p) => s + p.morale, 0) / activePeople.length
      : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-100">{company.name}</h1>
        <p className="text-sm text-zinc-500">
          {status
            ? `${t("simulation.currentQuarter")}: ${status.current_quarter}`
            : ""}
          {status && status.history_length > 0
            ? ` · ${status.history_length} ${t("simulation.historyLength")}`
            : ""}
          {status?.enhanced_mode && (
            <span className="ml-2 text-emerald-500">
              ● {t("simulation.enhanced")}
            </span>
          )}
        </p>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-5 gap-4">
        <MetricCard
          label={t("dashboard.activePeople")}
          value={activePeople.length}
          sub={
            departedPeople.length > 0
              ? `${departedPeople.length} ${t("dashboard.departed").toLowerCase()}`
              : `${company.department_count} depts`
          }
        />
        <MetricCard
          label={t("dashboard.avgTenure")}
          value={`${company.avg_tenure}${t("dashboard.years")}`}
          sub={`${company.role_count} roles`}
        />
        <MetricCard
          label={t("dashboard.avgBurnout")}
          value={`${(company.avg_burnout_risk * 100).toFixed(0)}%`}
          color={burnoutColor(company.avg_burnout_risk)}
        />
        <MetricCard
          label={t("dashboard.avgMorale")}
          value={`${(avgMorale * 100).toFixed(0)}%`}
          color={moraleColor(avgMorale)}
        />
        <MetricCard
          label={t("dashboard.skills")}
          value={company.skill_count}
          sub="tracked"
        />
      </div>

      {/* Company Score History */}
      {scoreHistory.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-zinc-300">
              <TrendingUp size={14} className="inline mr-1.5" />
              {t("dashboard.scoreHistory")}
            </h2>
            <span
              className={`text-lg font-bold ${scoreColor(scoreHistory[scoreHistory.length - 1].total)}`}
            >
              {scoreHistory[scoreHistory.length - 1].total}
            </span>
          </div>
          <div className="flex items-end gap-1 h-16">
            {scoreHistory.slice(-12).map((entry) => (
              <div
                key={entry.quarter}
                className="flex-1 flex flex-col items-center gap-0.5"
              >
                <div
                  className={`w-full rounded-sm ${scoreBg(entry.total)}`}
                  style={{ height: `${Math.max(4, entry.total * 0.6)}px` }}
                />
                <span className="text-[8px] text-zinc-600">
                  {entry.quarter.split("-")[1]}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Milestones Grid */}
      {achievements.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl">
          <div className="px-4 py-3 border-b border-zinc-800 flex items-center gap-2">
            <Award size={14} className="text-amber-400" />
            <h2 className="text-sm font-semibold text-zinc-300">
              {t("dashboard.milestones")}
            </h2>
            {achievementProgress && (
              <span className="ml-auto text-xs text-zinc-500">
                {achievementProgress.unlocked}/{achievementProgress.total} (
                {achievementProgress.percentage}%)
              </span>
            )}
          </div>
          <div className="grid grid-cols-3 gap-2 p-3">
            {achievements.map((a) => (
              <div
                key={a.id}
                className={`p-3 rounded-lg border ${
                  a.unlocked
                    ? "bg-emerald-500/10 border-emerald-500/20"
                    : "bg-zinc-800/50 border-zinc-800 opacity-50"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">{a.icon}</span>
                  <div>
                    <p className="text-xs font-medium text-zinc-200">
                      {lang === "ko" ? a.name_ko : a.name}
                    </p>
                    <p className="text-[10px] text-zinc-500">
                      {lang === "ko" ? a.description_ko : a.description}
                    </p>
                    {a.unlocked && a.unlocked_at && (
                      <p className="text-[10px] text-emerald-500 mt-0.5">
                        ✓ {a.unlocked_at}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* People Overview */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl">
        <div className="px-4 py-3 border-b border-zinc-800">
          <h2 className="text-sm font-semibold text-zinc-300">
            {t("dashboard.teamOverview")}
          </h2>
        </div>
        <div className="divide-y divide-zinc-800">
          {people.map((p) => (
            <div
              key={p.id}
              className={`px-4 py-3 flex items-center justify-between hover:bg-zinc-800/50 transition-colors ${p.departed ? "opacity-40" : ""}`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${p.departed ? "bg-red-900/40 text-red-500" : "bg-zinc-800 text-zinc-400"}`}
                >
                  {p.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
                <div>
                  <p className="text-sm font-medium text-zinc-200">
                    {p.name}
                    {p.departed && (
                      <span className="ml-2 text-xs text-red-400">
                        {t("dashboard.departed").toLowerCase()}
                      </span>
                    )}
                  </p>
                  <p className="text-xs text-zinc-500">
                    {p.active_role || "Unassigned"} ·{" "}
                    {p.active_department || "—"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {/* Morale bar */}
                {!p.departed && (
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-zinc-500">
                      {t("dashboard.morale")}
                    </span>
                    <div className="w-16 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${moraleBg(p.morale)}`}
                        style={{ width: `${p.morale * 100}%` }}
                      />
                    </div>
                    <span
                      className={`text-xs font-mono ${moraleColor(p.morale)}`}
                    >
                      {(p.morale * 100).toFixed(0)}
                    </span>
                  </div>
                )}
                <span className="text-xs text-zinc-500">
                  {p.tenure_years}
                  {t("dashboard.years")}
                </span>
                <BurnoutBadge risk={p.burnout_risk} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Alerts */}
      <div className="grid grid-cols-2 gap-4">
        {/* Burnout Alerts */}
        {burnoutWarnings.length > 0 && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-red-400 mb-2">
              {t("dashboard.burnoutWarnings")} ({burnoutWarnings.length})
            </h3>
            <div className="space-y-1">
              {burnoutWarnings.map((p) => (
                <p key={p.id} className="text-sm text-zinc-300">
                  <span className={burnoutColor(p.burnout_risk)}>
                    {p.name}
                  </span>{" "}
                  — {(p.burnout_risk * 100).toFixed(0)}%
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Low Morale Alerts */}
        {lowMorale.length > 0 && (
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-amber-400 mb-2">
              {t("dashboard.lowMorale")} ({lowMorale.length})
            </h3>
            <div className="space-y-1">
              {lowMorale.map((p) => (
                <p key={p.id} className="text-sm text-zinc-300">
                  <span className={moraleColor(p.morale)}>{p.name}</span> —{" "}
                  {(p.morale * 100).toFixed(0)}%{" "}
                  {t("dashboard.morale").toLowerCase()}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Departed */}
        {departedPeople.length > 0 && (
          <div className="bg-zinc-800/50 border border-zinc-700 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-zinc-400 mb-2">
              {t("dashboard.departed")} ({departedPeople.length})
            </h3>
            <div className="space-y-1">
              {departedPeople.map((p) => (
                <p key={p.id} className="text-sm text-zinc-500">
                  {p.name} — was {p.active_role || "unassigned"}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
