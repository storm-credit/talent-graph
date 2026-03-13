import { ResponsiveRadar } from "@nivo/radar";
import type { SkillInfo } from "../types";

const levelToNumber: Record<string, number> = {
  novice: 1,
  beginner: 2,
  intermediate: 3,
  advanced: 4,
  expert: 5,
};

interface SkillRadarProps {
  skills: SkillInfo[];
}

export function SkillRadar({ skills }: SkillRadarProps) {
  if (skills.length === 0) return null;

  const data = skills.map((s) => ({
    skill: s.name,
    level: levelToNumber[s.person_level || "novice"] || 1,
  }));

  return (
    <div className="h-64 w-full">
      <ResponsiveRadar
        data={data}
        keys={["level"]}
        indexBy="skill"
        maxValue={5}
        margin={{ top: 30, right: 60, bottom: 30, left: 60 }}
        borderColor={{ from: "color" }}
        gridLevels={5}
        gridShape="circular"
        gridLabelOffset={16}
        dotSize={8}
        dotColor={{ theme: "background" }}
        dotBorderWidth={2}
        colors={["#10b981"]}
        fillOpacity={0.25}
        blendMode="normal"
        animate={true}
        theme={{
          text: { fill: "#a1a1aa", fontSize: 11 },
          grid: { line: { stroke: "#3f3f46", strokeWidth: 1 } },
          tooltip: {
            container: {
              background: "#18181b",
              color: "#e4e4e7",
              border: "1px solid #3f3f46",
              fontSize: 12,
            },
          },
        }}
      />
    </div>
  );
}
