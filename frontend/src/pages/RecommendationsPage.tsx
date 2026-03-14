import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import type { PersonSummary, Recommendation, PlacementCell } from "../types";
import { motion, AnimatePresence } from "framer-motion";
import { Target, Users, Grid3x3 } from "lucide-react";
import { fitColor } from "../lib/utils";

type Tab = "person" | "vacancies" | "matrix";

export function RecommendationsPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const [tab, setTab] = useState<Tab>("person");
  const [people, setPeople] = useState<PersonSummary[]>([]);
  const [selectedPerson, setSelectedPerson] = useState<string>("");
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [matrix, setMatrix] = useState<PlacementCell[]>([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    api.getPeople().then((p) => setPeople(p.filter((x) => !x.departed)));
  }, []);

  const handlePersonSelect = async (personId: string) => {
    setSelectedPerson(personId);
    if (!personId) return;
    setLoadingRecs(true);
    try {
      const recs = await api.getRecommendationsForPerson(personId);
      setRecommendations(recs);
    } catch {
      setRecommendations([]);
    }
    setLoadingRecs(false);
  };

  const loadMatrix = async () => {
    try {
      const m = await api.getPlacementMatrix();
      setMatrix(m);
    } catch {
      setMatrix([]);
    }
  };

  useEffect(() => {
    if (tab === "matrix" && matrix.length === 0) loadMatrix();
  }, [tab]);

  const tabs = [
    { id: "person" as Tab, icon: Target, label: t("recommendations.bestFit") },
    { id: "matrix" as Tab, icon: Grid3x3, label: t("recommendations.matrix") },
  ];

  // Group matrix by person for heatmap display
  const matrixPersons = [...new Set(matrix.map((c) => c.person_name))];
  const matrixRoles = [...new Set(matrix.map((c) => `${c.role_title}`))];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-100">
          {t("recommendations.title")}
        </h1>
        <p className="text-sm text-zinc-500">
          {t("recommendations.subtitle")}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-zinc-900 p-1 rounded-lg w-fit">
        {tabs.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors ${
              tab === id
                ? "bg-emerald-500/15 text-emerald-400"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>

      {/* Best Fit Tab */}
      {tab === "person" && (
        <div className="space-y-4">
          <select
            value={selectedPerson}
            onChange={(e) => handlePersonSelect(e.target.value)}
            className="bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">{t("recommendations.selectPerson")}</option>
            {people.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} — {p.active_role || "Unassigned"}
              </option>
            ))}
          </select>

          {loadingRecs && (
            <p className="text-sm text-zinc-500">{t("common.loading")}</p>
          )}

          <AnimatePresence>
            {recommendations.map((rec, i) => (
              <motion.div
                key={`${rec.role_id}-${rec.department_id}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-xs text-zinc-500">#{i + 1}</span>
                    <h3 className="text-sm font-semibold text-zinc-200">
                      {rec.role_title}
                    </h3>
                    <p className="text-xs text-zinc-500">{rec.department_name}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${fitColor(rec.fit_score)}`}>
                      {(rec.fit_score * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-zinc-500">
                      {t("recommendations.growthPotential")}: {rec.growth_potential}
                    </p>
                  </div>
                </div>

                {/* Strengths & Gaps */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs font-medium text-emerald-400 mb-1">
                      {t("recommendations.strengths")}
                    </p>
                    {rec.strengths.map((s, j) => (
                      <p key={j} className="text-xs text-zinc-400">
                        ✓ {s}
                      </p>
                    ))}
                  </div>
                  <div>
                    <p className="text-xs font-medium text-amber-400 mb-1">
                      {t("recommendations.gaps")}
                    </p>
                    {rec.gaps.map((g, j) => (
                      <p key={j} className="text-xs text-zinc-400">
                        ✗ {g}
                      </p>
                    ))}
                    {rec.gaps.length === 0 && (
                      <p className="text-xs text-zinc-600">
                        {t("recommendations.noGaps")}
                      </p>
                    )}
                  </div>
                </div>

                <p className="text-xs text-zinc-500 italic">
                  {lang === "ko" ? rec.recommendation_ko : rec.recommendation_en}
                </p>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Matrix Tab */}
      {tab === "matrix" && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-auto">
          {matrix.length === 0 ? (
            <p className="p-4 text-sm text-zinc-500">{t("common.loading")}</p>
          ) : (
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="px-3 py-2 text-left text-zinc-500">
                    {t("recommendations.person")}
                  </th>
                  {matrixRoles.map((role) => (
                    <th
                      key={role}
                      className="px-2 py-2 text-center text-zinc-500 whitespace-nowrap"
                    >
                      {role}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrixPersons.map((person) => (
                  <tr key={person} className="border-b border-zinc-800/50">
                    <td className="px-3 py-2 text-zinc-300 whitespace-nowrap">
                      {person}
                    </td>
                    {matrixRoles.map((role) => {
                      const cell = matrix.find(
                        (c) => c.person_name === person && c.role_title === role,
                      );
                      const score = cell ? cell.fit_score : 0;
                      const intensity = Math.round(score * 100);
                      return (
                        <td
                          key={`${person}-${role}`}
                          className="px-2 py-2 text-center"
                        >
                          <span
                            className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-mono ${
                              score >= 0.7
                                ? "bg-emerald-500/20 text-emerald-400"
                                : score >= 0.5
                                  ? "bg-amber-500/20 text-amber-400"
                                  : "bg-zinc-800 text-zinc-500"
                            }`}
                          >
                            {intensity}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
