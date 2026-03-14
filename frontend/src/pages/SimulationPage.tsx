import { useEffect, useState } from "react";
import { useSimulationStore } from "../store/simulation";
import type { ChangeRecord } from "../types";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, SkipBack } from "lucide-react";
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

export function SimulationPage() {
  const {
    status,
    lastAdvance,
    allChanges,
    loading,
    fetchStatus,
    advance,
    rollback,
    reset,
  } = useSimulationStore();
  const [animatingChanges, setAnimatingChanges] = useState<ChangeRecord[]>([]);

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleAdvance = async () => {
    const result = await advance();
    // Stagger animation
    setAnimatingChanges([]);
    for (let i = 0; i < result.changes.length; i++) {
      setTimeout(() => {
        setAnimatingChanges((prev) => [...prev, result.changes[i]]);
      }, i * 80);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">Simulation</h1>
          <p className="text-sm text-zinc-500">
            {status
              ? `Quarter ${status.current_quarter} · ${status.history_length} simulated`
              : "Loading..."}
            {status?.enhanced_mode && (
              <span className="ml-2 text-emerald-500">● Enhanced</span>
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
            Rollback
          </button>
          <button
            onClick={reset}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-zinc-800 text-zinc-300 text-sm hover:bg-zinc-700 disabled:opacity-30 transition-colors"
          >
            <RotateCcw size={14} />
            Reset
          </button>
          <button
            onClick={handleAdvance}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 disabled:opacity-50 transition-colors"
          >
            <Play size={14} />
            {loading ? "Simulating..." : "Advance Quarter"}
          </button>
        </div>
      </div>

      {/* Stats bar */}
      {status && (
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
            <p className="text-xs text-zinc-500">Active</p>
            <p className="text-lg font-bold text-zinc-100">
              {status.active_people}
            </p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
            <p className="text-xs text-zinc-500">Departed</p>
            <p className="text-lg font-bold text-red-400">
              {status.departed_people}
            </p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
            <p className="text-xs text-zinc-500">Avg Morale</p>
            <p
              className={`text-lg font-bold ${status.average_morale >= 0.7 ? "text-emerald-400" : status.average_morale >= 0.4 ? "text-amber-400" : "text-red-400"}`}
            >
              {(status.average_morale * 100).toFixed(0)}%
            </p>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
            <p className="text-xs text-zinc-500">Quarters</p>
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
              ? `Changes from ${lastAdvance.quarter} (${animatingChanges.length})`
              : "No simulation run yet"}
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
              Click &quot;Advance Quarter&quot; to simulate the next quarter
            </div>
          )}
        </div>
      </div>

      {/* Full History */}
      {allChanges.length > 0 && lastAdvance && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl">
          <div className="px-4 py-3 border-b border-zinc-800">
            <h2 className="text-sm font-semibold text-zinc-300">
              Full History ({allChanges.length} events)
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
    </div>
  );
}
