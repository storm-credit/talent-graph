import { AnimatePresence, motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { PixelCharacter, type CharacterMood } from "./PixelCharacter";
import { PixelDesk } from "./PixelDesk";
import { FloatingEffect } from "./FloatingEffect";
import { useGameModeStore } from "../../store/gameMode";

const DEPT_COLORS: Record<string, { floor: string; wall: string; shirt: string }> = {
  "Data Engineering": { floor: "#1a2a1a", wall: "#2d4a2d", shirt: "#4CAF50" },
  "Data Science": { floor: "#1a1a2a", wall: "#2d2d5a", shirt: "#5C6BC0" },
  Finance: { floor: "#2a1a1a", wall: "#5a2d2d", shirt: "#EF5350" },
  "Engineering Management": { floor: "#2a2a1a", wall: "#4a4a2d", shirt: "#FF9800" },
  Marketing: { floor: "#1a2a2a", wall: "#2d4a4a", shirt: "#26C6DA" },
  Sales: { floor: "#2a1a2a", wall: "#4a2d4a", shirt: "#AB47BC" },
  Unassigned: { floor: "#1a1a1a", wall: "#333", shirt: "#888" },
};

function getDeptStyle(dept: string) {
  return DEPT_COLORS[dept] || DEPT_COLORS["Unassigned"];
}

const SKIN_COLORS = ["#FFCC99", "#F5C49C", "#D4A57B", "#C68642", "#8D5524"];

function personSkin(name: string): string {
  let hash = 0;
  for (const ch of name) hash = ((hash << 5) - hash + ch.charCodeAt(0)) | 0;
  return SKIN_COLORS[Math.abs(hash) % SKIN_COLORS.length];
}

function getMood(
  morale: number,
  burnout: number,
  departed: boolean,
  hasEffect: boolean,
  effectType?: string,
): CharacterMood {
  if (departed || effectType === "departure") return "departing";
  if (effectType === "skill_growth" || effectType === "certification")
    return "celebrating";
  if (effectType === "outcome") return "happy";
  if (burnout > 0.7) return "burnout";
  if (morale < 0.3) return "stressed";
  if (morale > 0.75 && hasEffect) return "happy";
  return "working";
}

export function WorkspaceGrid() {
  const { t } = useTranslation();
  const { departmentGroups, localPeople, activeEffects, speed } =
    useGameModeStore();

  const deptEntries = Object.entries(departmentGroups).sort(([a], [b]) =>
    a.localeCompare(b),
  );

  if (deptEntries.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-zinc-600 text-sm">
        {t("common.loading")}
      </div>
    );
  }

  const pixelScale = 3;

  return (
    <div className="flex-1 overflow-y-auto space-y-4 pr-2">
      {deptEntries.map(([dept, people]) => {
        const style = getDeptStyle(dept);
        const activePeople = people.filter(
          (p) => !localPeople[p.id]?.departed,
        );

        return (
          <div key={dept} className="rounded-xl overflow-hidden border border-zinc-800">
            {/* Department "room" header - wall */}
            <div
              className="px-4 py-2 flex items-center gap-2"
              style={{ backgroundColor: style.wall }}
            >
              <div
                className="w-2 h-2 rounded-sm"
                style={{ backgroundColor: style.shirt }}
              />
              <span className="text-xs font-bold text-zinc-200 uppercase tracking-wider">
                {dept}
              </span>
              <span className="text-[10px] text-zinc-400 ml-1">
                ({activePeople.length})
              </span>
            </div>

            {/* Office floor */}
            <div
              className="relative px-6 py-6"
              style={{
                backgroundColor: style.floor,
                backgroundImage:
                  "radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px)",
                backgroundSize: "16px 16px",
              }}
            >
              {/* Floor tiles pattern */}
              <div className="flex flex-wrap gap-8 justify-start items-end">
                <AnimatePresence>
                  {activePeople.map((p, i) => {
                    const lp = localPeople[p.id] || p;
                    const effect = activeEffects[p.id] || null;
                    const mood = getMood(
                      lp.morale,
                      lp.burnout_risk,
                      lp.departed,
                      !!effect,
                      effect?.change.change_type,
                    );

                    return (
                      <motion.div
                        key={p.id}
                        layoutId={`desk-${p.id}`}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, x: 80, scale: 0.5 }}
                        transition={{
                          type: "spring",
                          damping: 20,
                          delay: i * 0.05,
                        }}
                        className="relative flex flex-col items-center"
                      >
                        {/* Floating effect */}
                        {effect && (
                          <div className="absolute -top-8 left-1/2 -translate-x-1/2 z-20">
                            <FloatingEffect
                              change={effect.change}
                              speed={speed}
                            />
                          </div>
                        )}

                        {/* Character sitting at desk */}
                        <div className="relative">
                          {/* Character (positioned behind desk) */}
                          <div
                            style={{
                              marginBottom: -2 * pixelScale,
                              position: "relative",
                              zIndex: 1,
                            }}
                          >
                            <PixelCharacter
                              name={lp.name}
                              mood={mood}
                              shirtColor={style.shirt}
                              skinColor={personSkin(lp.name)}
                              direction={i % 2 === 0 ? "right" : "left"}
                              size={pixelScale}
                            />
                          </div>

                          {/* Desk (in front of character) */}
                          <div style={{ position: "relative", zIndex: 2, marginTop: -6 }}>
                            <PixelDesk size={pixelScale} />
                          </div>
                        </div>

                        {/* Role label */}
                        <p
                          className="text-[8px] text-zinc-500 text-center mt-1 truncate"
                          style={{ maxWidth: 16 * pixelScale }}
                        >
                          {lp.active_role || "—"}
                        </p>

                        {/* Morale/burnout indicators */}
                        <div className="flex gap-0.5 mt-0.5">
                          {/* Morale hearts */}
                          {Array.from(
                            { length: Math.round(lp.morale * 5) },
                            (_, j) => (
                              <div
                                key={j}
                                style={{
                                  width: 4,
                                  height: 4,
                                  backgroundColor:
                                    lp.morale > 0.6
                                      ? "#4CAF50"
                                      : lp.morale > 0.3
                                        ? "#FFC107"
                                        : "#F44336",
                                  borderRadius: 1,
                                }}
                              />
                            ),
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>

              {/* Room decorations */}
              <div
                className="absolute bottom-2 right-3 text-[8px] text-zinc-600 font-mono"
                style={{ imageRendering: "pixelated" }}
              >
                {dept}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
