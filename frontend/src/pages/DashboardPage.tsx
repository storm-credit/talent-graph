import { useEffect, useState } from "react";
import { api } from "../api";
import type { CompanyOverview, PersonSummary } from "../types";
import { MetricCard } from "../components/MetricCard";
import { BurnoutBadge } from "../components/BurnoutBadge";
import { burnoutColor } from "../lib/utils";
import { useSimulationStore } from "../store/simulation";

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

export function DashboardPage() {
  const [company, setCompany] = useState<CompanyOverview | null>(null);
  const [people, setPeople] = useState<PersonSummary[]>([]);
  const status = useSimulationStore((s) => s.status);
  const fetchStatus = useSimulationStore((s) => s.fetchStatus);

  useEffect(() => {
    api.getCompany().then(setCompany);
    api.getPeople().then(setPeople);
    fetchStatus();
  }, []);

  if (!company) return <div className="text-zinc-500">Loading...</div>;

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
          {status ? `Current: ${status.current_quarter}` : ""}
          {status && status.history_length > 0
            ? ` · ${status.history_length} quarters simulated`
            : ""}
          {status?.enhanced_mode && (
            <span className="ml-2 text-emerald-500">● Enhanced Mode</span>
          )}
        </p>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-5 gap-4">
        <MetricCard
          label="Active"
          value={activePeople.length}
          sub={
            departedPeople.length > 0
              ? `${departedPeople.length} departed`
              : `${company.department_count} depts`
          }
        />
        <MetricCard
          label="Avg Tenure"
          value={`${company.avg_tenure}y`}
          sub={`${company.role_count} roles`}
        />
        <MetricCard
          label="Avg Burnout"
          value={`${(company.avg_burnout_risk * 100).toFixed(0)}%`}
          color={burnoutColor(company.avg_burnout_risk)}
        />
        <MetricCard
          label="Avg Morale"
          value={`${(avgMorale * 100).toFixed(0)}%`}
          color={moraleColor(avgMorale)}
        />
        <MetricCard
          label="Skills"
          value={company.skill_count}
          sub="tracked"
        />
      </div>

      {/* People Overview */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl">
        <div className="px-4 py-3 border-b border-zinc-800">
          <h2 className="text-sm font-semibold text-zinc-300">
            Team Overview
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
                        departed
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
                    <span className="text-xs text-zinc-500">Morale</span>
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
                  {p.tenure_years}y
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
              Burnout Warnings ({burnoutWarnings.length})
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
              Low Morale ({lowMorale.length})
            </h3>
            <div className="space-y-1">
              {lowMorale.map((p) => (
                <p key={p.id} className="text-sm text-zinc-300">
                  <span className={moraleColor(p.morale)}>{p.name}</span> —{" "}
                  {(p.morale * 100).toFixed(0)}% morale
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Departed */}
        {departedPeople.length > 0 && (
          <div className="bg-zinc-800/50 border border-zinc-700 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-zinc-400 mb-2">
              Departed ({departedPeople.length})
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
