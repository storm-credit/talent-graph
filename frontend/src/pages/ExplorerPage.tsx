import { useEffect, useState } from "react";
import { api } from "../api";
import type { FitResult, PersonSummary, ScoringWeights } from "../types";
import { FitBadge } from "../components/FitBadge";
import { fitColor } from "../lib/utils";

const WEIGHT_LABELS: Record<keyof ScoringWeights, string> = {
  skill_match: "Skill Match",
  historical_performance: "Historical Performance",
  level_match: "Level Match",
  burnout_risk: "Burnout Risk",
};

export function ExplorerPage() {
  const [weights, setWeights] = useState<ScoringWeights>({
    skill_match: 0.4,
    historical_performance: 0.3,
    level_match: 0.15,
    burnout_risk: 0.15,
  });
  const [people, setPeople] = useState<PersonSummary[]>([]);
  const [selectedPerson, setSelectedPerson] = useState<string>("");
  const [results, setResults] = useState<FitResult[]>([]);
  const [origResults, setOrigResults] = useState<FitResult[]>([]);

  useEffect(() => {
    api.getWeights().then(setWeights);
    api.getPeople().then((p) => {
      setPeople(p);
      if (p.length > 0) setSelectedPerson(p[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedPerson) {
      api.evaluatePerson(selectedPerson).then((r) => {
        setResults(r);
        if (origResults.length === 0) setOrigResults(r);
      });
    }
  }, [selectedPerson]);

  const applyWeights = async () => {
    await api.updateWeights(weights);
    if (selectedPerson) {
      const r = await api.evaluatePerson(selectedPerson);
      setResults(r);
    }
  };

  const handleWeightChange = (key: keyof ScoringWeights, value: number) => {
    setWeights((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-zinc-100">Score Explorer</h1>

      <div className="grid grid-cols-3 gap-6">
        {/* Weight Sliders */}
        <div className="col-span-1 bg-zinc-900 border border-zinc-800 rounded-xl p-5 space-y-5">
          <h2 className="text-sm font-semibold text-zinc-300">
            Scoring Weights
          </h2>
          {(Object.keys(WEIGHT_LABELS) as (keyof ScoringWeights)[]).map(
            (key) => (
              <div key={key} className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-zinc-400">{WEIGHT_LABELS[key]}</span>
                  <span className="text-zinc-300 font-mono">
                    {weights[key].toFixed(2)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={weights[key]}
                  onChange={(e) =>
                    handleWeightChange(key, parseFloat(e.target.value))
                  }
                  className="w-full h-1.5 bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
              </div>
            )
          )}
          <button
            onClick={applyWeights}
            className="w-full py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors"
          >
            Apply Weights
          </button>

          <div className="pt-3 border-t border-zinc-800">
            <label className="text-xs text-zinc-500">Person</label>
            <select
              value={selectedPerson}
              onChange={(e) => setSelectedPerson(e.target.value)}
              className="mt-1 w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-emerald-500"
            >
              {people.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Results Comparison */}
        <div className="col-span-2 bg-zinc-900 border border-zinc-800 rounded-xl">
          <div className="px-4 py-3 border-b border-zinc-800">
            <h2 className="text-sm font-semibold text-zinc-300">
              Fit Results
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 text-xs text-zinc-500">
                  <th className="text-left px-4 py-2">Role</th>
                  <th className="text-left px-4 py-2">Dept</th>
                  <th className="text-right px-4 py-2">Fit</th>
                  <th className="text-right px-4 py-2">Skill</th>
                  <th className="text-right px-4 py-2">History</th>
                  <th className="text-right px-4 py-2">Level</th>
                  <th className="text-right px-4 py-2">Burnout</th>
                  <th className="text-right px-4 py-2">Perf</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/50">
                {results.map((r) => {
                  const orig = origResults.find(
                    (o) =>
                      o.role_id === r.role_id &&
                      o.department_id === r.department_id
                  );
                  const diff = orig
                    ? r.fit_score - orig.fit_score
                    : 0;
                  return (
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
                        <div className="flex items-center justify-end gap-2">
                          <FitBadge score={r.fit_score} size="sm" />
                          {Math.abs(diff) > 0.005 && (
                            <span
                              className={`text-xs font-mono ${diff > 0 ? "text-emerald-400" : "text-red-400"}`}
                            >
                              {diff > 0 ? "+" : ""}
                              {(diff * 100).toFixed(0)}
                            </span>
                          )}
                        </div>
                      </td>
                      <td
                        className={`px-4 py-2 text-right font-mono text-xs ${fitColor(r.skill_match_score)}`}
                      >
                        {(r.skill_match_score * 100).toFixed(0)}
                      </td>
                      <td className="px-4 py-2 text-right font-mono text-xs text-zinc-400">
                        {(r.historical_score * 100).toFixed(0)}
                      </td>
                      <td className="px-4 py-2 text-right font-mono text-xs text-zinc-400">
                        {(r.level_match_score * 100).toFixed(0)}
                      </td>
                      <td className="px-4 py-2 text-right font-mono text-xs text-amber-400">
                        {(r.burnout_risk_score * 100).toFixed(0)}
                      </td>
                      <td className="px-4 py-2 text-right font-mono text-xs text-zinc-300">
                        {r.predicted_performance.toFixed(1)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
