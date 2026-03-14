import { motion } from "framer-motion";
import type { ChangeRecord } from "../../types";

interface Props {
  change: ChangeRecord;
  speed: number;
}

function effectContent(change: ChangeRecord): { icon: string; text: string; color: string } {
  switch (change.change_type) {
    case "skill_growth":
      return { icon: "✨", text: change.description.split(":").pop()?.trim() || "Skill UP", color: "text-cyan-400" };
    case "skill_decay":
      return { icon: "📉", text: "Skill ↓", color: "text-orange-400" };
    case "morale_change":
      return {
        icon: parseFloat(change.new_value || "0") > parseFloat(change.old_value || "0") ? "😊" : "😟",
        text: `${((parseFloat(change.old_value || "0")) * 100).toFixed(0)}→${((parseFloat(change.new_value || "0")) * 100).toFixed(0)}%`,
        color: parseFloat(change.new_value || "0") > parseFloat(change.old_value || "0") ? "text-emerald-400" : "text-red-400",
      };
    case "burnout_change":
      return {
        icon: "🔥",
        text: `${((parseFloat(change.new_value || "0")) * 100).toFixed(0)}%`,
        color: parseFloat(change.new_value || "0") > 0.6 ? "text-red-400" : "text-amber-400",
      };
    case "outcome":
      return {
        icon: change.rating === "exceeds" || change.rating === "exceptional" ? "⭐" : change.rating === "meets" ? "✅" : "⚠️",
        text: change.rating || "",
        color: change.rating === "exceeds" || change.rating === "exceptional" ? "text-amber-400" : change.rating === "meets" ? "text-zinc-300" : "text-red-400",
      };
    case "departure":
      return { icon: "👋", text: "Departed", color: "text-red-400" };
    case "certification":
      return { icon: "🏅", text: "Certified!", color: "text-cyan-400" };
    case "mentoring":
      return { icon: "🤝", text: "Mentoring", color: "text-indigo-400" };
    case "personal_event":
      return { icon: "💬", text: change.description.split(":").pop()?.trim() || "Event", color: "text-yellow-400" };
    default:
      return { icon: "📌", text: change.change_type, color: "text-zinc-400" };
  }
}

export function FloatingEffect({ change, speed }: Props) {
  const { icon, text, color } = effectContent(change);
  const duration = Math.max(1.0 / speed, 0.4);

  return (
    <motion.div
      initial={{ y: 0, opacity: 1, scale: 0.8 }}
      animate={{ y: -48, opacity: 0, scale: 1 }}
      transition={{ duration, ease: "easeOut" }}
      className={`absolute -top-2 left-1/2 -translate-x-1/2 z-20 pointer-events-none whitespace-nowrap`}
    >
      <div className={`flex items-center gap-1 px-2 py-1 rounded-full bg-zinc-900/90 border border-zinc-700 shadow-lg text-xs font-semibold ${color}`}>
        <span>{icon}</span>
        <span className="capitalize">{text}</span>
      </div>
    </motion.div>
  );
}
