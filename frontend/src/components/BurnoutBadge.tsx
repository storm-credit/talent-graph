import { cn, burnoutColor, burnoutBg } from "../lib/utils";

interface BurnoutBadgeProps {
  risk: number;
}

export function BurnoutBadge({ risk }: BurnoutBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-mono font-semibold",
        burnoutColor(risk),
        burnoutBg(risk),
        risk > 0.6 && "animate-burnout-pulse"
      )}
    >
      {(risk * 100).toFixed(0)}% burn
    </span>
  );
}
