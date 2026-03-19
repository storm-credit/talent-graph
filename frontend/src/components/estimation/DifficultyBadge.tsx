const LABELS = ["", "Trivial", "Easy", "Moderate", "Hard", "Extreme"];
const COLORS = [
  "",
  "bg-zinc-700 text-zinc-300",
  "bg-emerald-900 text-emerald-300",
  "bg-amber-900 text-amber-300",
  "bg-orange-900 text-orange-300",
  "bg-red-900 text-red-300",
];

export function DifficultyBadge({ level }: { level: number }) {
  return (
    <span
      className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${COLORS[level] || COLORS[3]}`}
    >
      {"★".repeat(level)} {LABELS[level] || "?"}
    </span>
  );
}
