import { cn, fitColor, fitBg } from "../lib/utils";

interface FitBadgeProps {
  score: number;
  size?: "sm" | "md" | "lg";
}

export function FitBadge({ score, size = "md" }: FitBadgeProps) {
  const sizeClasses = {
    sm: "text-xs px-1.5 py-0.5",
    md: "text-sm px-2 py-0.5",
    lg: "text-base px-3 py-1",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border font-mono font-semibold",
        fitColor(score),
        fitBg(score),
        sizeClasses[size]
      )}
    >
      {(score * 100).toFixed(0)}
    </span>
  );
}
