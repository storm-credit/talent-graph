import { useEffect, useState } from "react";
import { api } from "../api";
import type { PersonDetail, PersonSummary } from "../types";
import { FitBadge } from "../components/FitBadge";
import { BurnoutBadge } from "../components/BurnoutBadge";
import { SkillRadar } from "../components/SkillRadar";
import { fitColor } from "../lib/utils";
import { motion, AnimatePresence } from "framer-motion";

export function PeoplePage() {
  const [people, setPeople] = useState<PersonSummary[]>([]);
  const [selected, setSelected] = useState<PersonDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getPeople().then(setPeople);
  }, []);

  const selectPerson = async (id: string) => {
    setLoading(true);
    const detail = await api.getPerson(id);
    setSelected(detail);
    setLoading(false);
  };

  return (
    <div className="flex gap-6 h-full">
      {/* Person List */}
      <div className="w-64 shrink-0 space-y-1">
        <h2 className="text-lg font-bold text-zinc-100 mb-3">People</h2>
        {people.map((p) => (
          <button
            key={p.id}
            onClick={() => selectPerson(p.id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg transition-colors ${
              selected?.id === p.id
                ? "bg-emerald-500/15 border border-emerald-500/30"
                : "hover:bg-zinc-800 border border-transparent"
            }`}
          >
            <p className="text-sm font-medium text-zinc-200">{p.name}</p>
            <p className="text-xs text-zinc-500">
              {p.active_role || "Unassigned"}
            </p>
          </button>
        ))}
      </div>

      {/* Person Detail */}
      <div className="flex-1 min-w-0">
        <AnimatePresence mode="wait">
          {selected ? (
            <motion.div
              key={selected.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-5"
            >
              {/* Header Card */}
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-zinc-100">
                      {selected.name}
                    </h2>
                    <p className="text-sm text-zinc-500">
                      {selected.active_role || "Unassigned"} ·{" "}
                      {selected.active_department || "—"}
                    </p>
                    <p className="text-xs text-zinc-600 mt-1">
                      {selected.tenure_years}y tenure · {selected.skills.length}{" "}
                      skills
                    </p>
                  </div>
                  <BurnoutBadge risk={selected.burnout_risk} />
                </div>
              </div>

              {/* Radar + Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                  <h3 className="text-xs text-zinc-500 uppercase tracking-wider mb-2">
                    Skill Profile
                  </h3>
                  <SkillRadar skills={selected.skills} />
                </div>
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                  <h3 className="text-xs text-zinc-500 uppercase tracking-wider mb-3">
                    Skills
                  </h3>
                  <div className="space-y-2">
                    {selected.skills.map((s) => (
                      <div
                        key={s.id}
                        className="flex items-center justify-between"
                      >
                        <span className="text-sm text-zinc-300">{s.name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-zinc-500 capitalize">
                            {s.person_level}
                          </span>
                          <div className="flex gap-0.5">
                            {[1, 2, 3, 4, 5].map((i) => (
                              <div
                                key={i}
                                className={`w-2 h-2 rounded-full ${
                                  i <=
                                  (({
                                    novice: 1,
                                    beginner: 2,
                                    intermediate: 3,
                                    advanced: 4,
                                    expert: 5,
                                  } as Record<string, number>)[
                                    s.person_level || "novice"
                                  ] || 1)
                                    ? "bg-emerald-500"
                                    : "bg-zinc-700"
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Fit Results Table */}
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl">
                <div className="px-4 py-3 border-b border-zinc-800">
                  <h3 className="text-xs text-zinc-500 uppercase tracking-wider">
                    Role Fit Scores
                  </h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-zinc-800 text-xs text-zinc-500">
                        <th className="text-left px-4 py-2">Role</th>
                        <th className="text-left px-4 py-2">Department</th>
                        <th className="text-right px-4 py-2">Fit</th>
                        <th className="text-right px-4 py-2">Skill</th>
                        <th className="text-right px-4 py-2">History</th>
                        <th className="text-right px-4 py-2">Level</th>
                        <th className="text-right px-4 py-2">Perf</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/50">
                      {selected.fit_results.slice(0, 8).map((r) => (
                        <tr
                          key={`${r.role_id}-${r.department_id}`}
                          className="hover:bg-zinc-800/30"
                        >
                          <td className="px-4 py-2 text-zinc-200">
                            {r.role_title}
                          </td>
                          <td className="px-4 py-2 text-zinc-400">
                            {r.department_name}
                          </td>
                          <td className="px-4 py-2 text-right">
                            <FitBadge score={r.fit_score} size="sm" />
                          </td>
                          <td
                            className={`px-4 py-2 text-right font-mono ${fitColor(r.skill_match_score)}`}
                          >
                            {(r.skill_match_score * 100).toFixed(0)}
                          </td>
                          <td className="px-4 py-2 text-right font-mono text-zinc-400">
                            {(r.historical_score * 100).toFixed(0)}
                          </td>
                          <td className="px-4 py-2 text-right font-mono text-zinc-400">
                            {(r.level_match_score * 100).toFixed(0)}
                          </td>
                          <td className="px-4 py-2 text-right font-mono text-zinc-300">
                            {r.predicted_performance.toFixed(1)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="flex items-center justify-center h-64 text-zinc-600">
              Select a person to view their profile
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
