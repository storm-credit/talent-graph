import { TrendingUp, TrendingDown, Minus } from "lucide-react";

const config = {
  rising: { Icon: TrendingUp, color: "text-emerald-400", label: "Rising" },
  declining: { Icon: TrendingDown, color: "text-red-400", label: "Declining" },
  stable: { Icon: Minus, color: "text-zinc-500", label: "Stable" },
};

export function TrendArrow({ trend }: { trend: string }) {
  const { Icon, color, label } = config[trend as keyof typeof config] || config.stable;
  return (
    <span className={`inline-flex items-center gap-0.5 ${color}`} title={label}>
      <Icon size={12} />
    </span>
  );
}
