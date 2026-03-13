import { cn } from "../lib/utils";

interface MetricCardProps {
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
}

export function MetricCard({ label, value, sub, color }: MetricCardProps) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
      <p className="text-xs text-zinc-500 uppercase tracking-wider">{label}</p>
      <p className={cn("text-2xl font-bold mt-1", color || "text-zinc-100")}>
        {value}
      </p>
      {sub && <p className="text-xs text-zinc-500 mt-0.5">{sub}</p>}
    </div>
  );
}
