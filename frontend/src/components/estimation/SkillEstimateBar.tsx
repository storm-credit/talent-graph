import { TrendArrow } from "./TrendArrow";
import type { SkillEstimate } from "../../types";

const LEVEL_NAMES = ["", "Novice", "Beginner", "Intermediate", "Advanced", "Expert"];

export function SkillEstimateBar({ est }: { est: SkillEstimate }) {
  const pct = ((est.mu - 1) / 4) * 100; // 1-5 → 0-100%
  const lo = Math.max(0, ((est.mu - 2 * est.sigma - 1) / 4) * 100);
  const hi = Math.min(100, ((est.mu + 2 * est.sigma - 1) / 4) * 100);

  const barColor =
    est.confidence > 70
      ? "bg-emerald-500"
      : est.confidence > 40
        ? "bg-amber-500"
        : "bg-zinc-500";

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs text-zinc-300 font-medium">
            {est.skill_name}
          </span>
          <TrendArrow trend={est.trend} />
        </div>
        <div className="flex items-center gap-2 text-[10px]">
          <span className="text-zinc-400">
            {est.level_name} ({est.mu.toFixed(1)})
          </span>
          <span
            className={`px-1 rounded ${
              est.confidence > 70
                ? "bg-emerald-900/50 text-emerald-400"
                : est.confidence > 40
                  ? "bg-amber-900/50 text-amber-400"
                  : "bg-zinc-800 text-zinc-500"
            }`}
          >
            {est.confidence.toFixed(0)}%
          </span>
          {est.official_level !== null && est.official_level !== undefined && (
            <span
              className={`px-1 rounded text-[10px] ${
                Math.abs(est.discrete_level - est.official_level) > 1
                  ? "bg-red-900/50 text-red-400"
                  : "bg-zinc-800 text-zinc-500"
              }`}
              title={`Official: ${LEVEL_NAMES[est.official_level]}`}
            >
              vs {LEVEL_NAMES[est.official_level]}
            </span>
          )}
        </div>
      </div>

      {/* Bar */}
      <div className="relative h-3 bg-zinc-800 rounded-full overflow-hidden">
        {/* Confidence interval band */}
        <div
          className="absolute top-0 h-full bg-zinc-700/50 rounded-full"
          style={{ left: `${lo}%`, width: `${hi - lo}%` }}
        />
        {/* Estimated level */}
        <div
          className={`absolute top-0 h-full ${barColor} rounded-full transition-all duration-300`}
          style={{ width: `${pct}%` }}
        />
        {/* Level markers */}
        {[1, 2, 3, 4].map((l) => (
          <div
            key={l}
            className="absolute top-0 h-full border-r border-zinc-600/30"
            style={{ left: `${(l / 4) * 100}%` }}
          />
        ))}
      </div>

      {/* Level scale */}
      <div className="flex justify-between text-[8px] text-zinc-600 px-0.5">
        {LEVEL_NAMES.slice(1).map((n) => (
          <span key={n}>{n}</span>
        ))}
      </div>
    </div>
  );
}
