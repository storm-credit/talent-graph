import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { AnimatePresence } from "framer-motion";
import { useGameModeStore } from "../store/gameMode";
import { PlaybackControls } from "../components/game/PlaybackControls";
import { WorkspaceGrid } from "../components/game/WorkspaceGrid";
import { EventBanner } from "../components/game/EventBanner";
import { QuarterSummaryPanel } from "../components/game/QuarterSummaryPanel";
import { motion } from "framer-motion";

export function GameModePage() {
  const { t } = useTranslation();
  const {
    fetchPeople,
    fetchStatus,
    playbackState,
    activeBanner,
    processedChanges,
    simStatus,
  } = useGameModeStore();

  useEffect(() => {
    fetchPeople();
    fetchStatus();
  }, []);

  const isFinished = playbackState === "finished";
  const isPlaying = playbackState === "playing" || playbackState === "paused";

  return (
    <div className="flex flex-col gap-4 relative" style={{ height: "calc(100vh - 3rem)" }}>
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">
            {t("game.title")}
          </h1>
          <p className="text-xs text-zinc-500">{t("game.subtitle")}</p>
        </div>
        {simStatus && (
          <div className="flex items-center gap-4 text-xs text-zinc-500">
            <span>
              {t("simulation.activePeople")}: <b className="text-zinc-300">{simStatus.active_people}</b>
            </span>
            <span>
              {t("simulation.departed")}: <b className="text-red-400">{simStatus.departed_people}</b>
            </span>
          </div>
        )}
      </div>

      {/* Main area */}
      <div className="flex-1 flex gap-4 min-h-0">
        {/* Left: Controls + Event Feed */}
        <div className="w-72 flex flex-col gap-4 shrink-0">
          <PlaybackControls />

          {/* Live event feed during playback */}
          {(isPlaying || isFinished) && processedChanges.length > 0 && (
            <div className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden flex flex-col">
              <div className="px-3 py-2 border-b border-zinc-800">
                <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
                  {t("game.eventLog")}
                </p>
              </div>
              <div className="flex-1 overflow-y-auto">
                <div className="divide-y divide-zinc-800/50">
                  {processedChanges
                    .slice()
                    .reverse()
                    .slice(0, 30)
                    .map((c, i) => (
                      <motion.div
                        key={`${c.person_id}-${c.change_type}-${i}`}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="px-3 py-2"
                      >
                        <div className="flex items-center gap-1.5">
                          <span className="text-[10px]">
                            {changeEmoji(c.change_type)}
                          </span>
                          <span className="text-[11px] text-zinc-300 font-medium truncate">
                            {c.person_name}
                          </span>
                        </div>
                        <p className="text-[10px] text-zinc-500 mt-0.5 truncate pl-4">
                          {c.description}
                        </p>
                      </motion.div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Center: Workspace */}
        <div className="flex-1 relative min-h-0">
          {/* Event Banner overlay */}
          <EventBanner banner={activeBanner} />

          <WorkspaceGrid />
        </div>

      </div>

      {/* Summary modal (shown when finished) */}
      <AnimatePresence>
        {isFinished && <QuarterSummaryPanel />}
      </AnimatePresence>
    </div>
  );
}

function changeEmoji(type: string): string {
  switch (type) {
    case "skill_growth": return "✨";
    case "skill_decay": return "📉";
    case "morale_change": return "💭";
    case "burnout_change": return "🔥";
    case "outcome": return "⭐";
    case "departure": return "👋";
    case "event": return "📢";
    case "certification": return "🏅";
    case "mentoring": return "🤝";
    case "personal_event": return "💬";
    default: return "📌";
  }
}
