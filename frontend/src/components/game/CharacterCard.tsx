import { motion } from "framer-motion";
import type { PersonSummary } from "../../types";
import type { ActiveEffect } from "../../store/gameMode";
import { FloatingEffect } from "./FloatingEffect";

interface Props {
  person: PersonSummary;
  effect: ActiveEffect | null;
  speed: number;
}

function moraleEmoji(morale: number): string {
  if (morale >= 0.8) return "😄";
  if (morale >= 0.6) return "🙂";
  if (morale >= 0.4) return "😐";
  if (morale >= 0.2) return "😟";
  return "😫";
}

function moraleBorder(morale: number): string {
  if (morale >= 0.7) return "border-emerald-500/40";
  if (morale >= 0.4) return "border-amber-500/40";
  return "border-red-500/40";
}

function initials(name: string): string {
  return name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function CharacterCard({ person, effect, speed }: Props) {
  const isDeparting = effect?.change.change_type === "departure";
  const isBurnoutHigh = person.burnout_risk > 0.7;
  const hasEffect = effect !== null;

  return (
    <motion.div
      layout
      layoutId={person.id}
      initial={{ opacity: 1, scale: 1 }}
      animate={{
        opacity: isDeparting ? 0.3 : 1,
        scale: hasEffect ? 1.05 : 1,
        x: isDeparting ? 60 : 0,
      }}
      exit={{ opacity: 0, x: 80, scale: 0.8 }}
      transition={{ type: "spring", damping: 20, stiffness: 300 }}
      className={`relative bg-zinc-900 border ${moraleBorder(person.morale)} rounded-xl p-3 flex flex-col items-center gap-1.5 min-w-[100px] ${
        hasEffect ? "ring-1 ring-emerald-500/30 shadow-lg shadow-emerald-500/10" : ""
      }`}
    >
      {/* Burnout pulse overlay */}
      {isBurnoutHigh && (
        <div className="absolute inset-0 rounded-xl bg-red-500/10 animate-pulse pointer-events-none" />
      )}

      {/* Floating effect */}
      {effect && <FloatingEffect change={effect.change} speed={speed} />}

      {/* Avatar */}
      <div
        className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
          person.departed
            ? "bg-zinc-700 text-zinc-500"
            : isBurnoutHigh
              ? "bg-red-500/20 text-red-400"
              : "bg-emerald-500/20 text-emerald-400"
        }`}
      >
        {initials(person.name)}
      </div>

      {/* Name */}
      <p className="text-xs font-medium text-zinc-200 text-center truncate w-full">
        {person.name}
      </p>

      {/* Role */}
      <p className="text-[10px] text-zinc-500 text-center truncate w-full">
        {person.active_role || "—"}
      </p>

      {/* Status bar */}
      <div className="flex items-center gap-2 text-[10px]">
        <span title="Morale">{moraleEmoji(person.morale)}</span>
        {isBurnoutHigh && <span title="Burnout High">🔥</span>}
      </div>

      {/* Morale bar */}
      <div className="w-full h-1 bg-zinc-800 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${
            person.morale >= 0.7
              ? "bg-emerald-500"
              : person.morale >= 0.4
                ? "bg-amber-500"
                : "bg-red-500"
          }`}
          initial={false}
          animate={{ width: `${person.morale * 100}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
    </motion.div>
  );
}
