import { useEffect, useState } from "react";
import { api } from "../api";
import type { CompanyOverview, PersonSummary } from "../types";
import { MetricCard } from "../components/MetricCard";
import { BurnoutBadge } from "../components/BurnoutBadge";
import { FitBadge } from "../components/FitBadge";
import { burnoutColor } from "../lib/utils";
import { useSimulationStore } from "../store/simulation";

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

  const burnoutWarnings = people.filter((p) => p.burnout_risk > 0.3);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-100">{company.name}</h1>
        <p className="text-sm text-zinc-500">
          {status ? `Current: ${status.current_quarter}` : ""}
          {status && status.history_length > 0
            ? ` · ${status.history_length} quarters simulated`
            : ""}
        </p>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          label="People"
          value={company.people_count}
          sub={`${company.department_count} departments`}
        />
        <MetricCard
          label="Avg Tenure"
          value={`${company.avg_tenure}y`}
          sub={`${company.role_count} roles`}
        />
        <MetricCard
          label="Avg Burnout Risk"
          value={`${(company.avg_burnout_risk * 100).toFixed(0)}%`}
          color={burnoutColor(company.avg_burnout_risk)}
        />
        <MetricCard
          label="Skills Tracked"
          value={company.skill_count}
          sub="across all categories"
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
              className="px-4 py-3 flex items-center justify-between hover:bg-zinc-800/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center text-xs font-bold text-zinc-400">
                  {p.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
                <div>
                  <p className="text-sm font-medium text-zinc-200">{p.name}</p>
                  <p className="text-xs text-zinc-500">
                    {p.active_role || "Unassigned"} ·{" "}
                    {p.active_department || "—"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-zinc-500">
                  {p.tenure_years}y tenure
                </span>
                <BurnoutBadge risk={p.burnout_risk} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Burnout Alerts */}
      {burnoutWarnings.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-red-400 mb-2">
            Burnout Warnings
          </h3>
          <div className="space-y-1">
            {burnoutWarnings.map((p) => (
              <p key={p.id} className="text-sm text-zinc-300">
                <span className={burnoutColor(p.burnout_risk)}>
                  {p.name}
                </span>{" "}
                — {(p.burnout_risk * 100).toFixed(0)}% risk in{" "}
                {p.active_role || "unassigned role"}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
