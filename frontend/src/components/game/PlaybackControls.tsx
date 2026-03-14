import { Play, Pause, SkipForward, RotateCcw } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useGameModeStore } from "../../store/gameMode";

export function PlaybackControls() {
  const { t } = useTranslation();
  const {
    playbackState,
    speed,
    currentChangeIndex,
    totalChanges,
    simStatus,
    startQuarter,
    setSpeed,
    pause,
    resume,
    skipToEnd,
    resetGame,
  } = useGameModeStore();

  const isPlaying = playbackState === "playing";
  const isIdle = playbackState === "idle";
  const isFinished = playbackState === "finished";
  const isPaused = playbackState === "paused";
  const isLoading = playbackState === "loading";
  const progress = totalChanges > 0 ? (currentChangeIndex / totalChanges) * 100 : 0;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
      {/* Quarter info */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-xs text-zinc-500">{t("game.currentQuarter")}</p>
          <p className="text-lg font-bold font-mono text-zinc-100">
            {simStatus?.current_quarter || "—"}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-zinc-500">{t("game.quartersPlayed")}</p>
          <p className="text-lg font-bold font-mono text-emerald-400">
            {simStatus?.history_length || 0}
          </p>
        </div>
      </div>

      {/* Progress bar */}
      {(isPlaying || isPaused || isFinished) && (
        <div className="mb-3">
          <div className="flex justify-between text-[10px] text-zinc-500 mb-1">
            <span>{t("game.events")}</span>
            <span>
              {currentChangeIndex}/{totalChanges}
            </span>
          </div>
          <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center gap-2">
        {/* Main action button */}
        {isIdle && (
          <button
            onClick={startQuarter}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors"
          >
            <Play size={16} fill="currentColor" />
            {t("game.startQuarter")}
          </button>
        )}
        {isLoading && (
          <button
            disabled
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-zinc-700 text-zinc-400 text-sm"
          >
            <div className="w-4 h-4 border-2 border-zinc-500 border-t-emerald-400 rounded-full animate-spin" />
            {t("common.loading")}
          </button>
        )}
        {isPlaying && (
          <button
            onClick={pause}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-amber-600 text-white text-sm font-medium hover:bg-amber-500 transition-colors"
          >
            <Pause size={16} />
            {t("game.pause")}
          </button>
        )}
        {isPaused && (
          <button
            onClick={resume}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors"
          >
            <Play size={16} fill="currentColor" />
            {t("game.resume")}
          </button>
        )}
        {isFinished && (
          <button
            onClick={startQuarter}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors"
          >
            <Play size={16} fill="currentColor" />
            {t("game.nextQuarter")}
          </button>
        )}

        {/* Skip */}
        {(isPlaying || isPaused) && (
          <button
            onClick={skipToEnd}
            className="p-2.5 rounded-lg bg-zinc-800 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700 transition-colors"
            title={t("game.skip")}
          >
            <SkipForward size={16} />
          </button>
        )}

        {/* Reset */}
        {isIdle && (
          <button
            onClick={resetGame}
            className="p-2.5 rounded-lg bg-zinc-800 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700 transition-colors"
            title={t("simulation.reset")}
          >
            <RotateCcw size={16} />
          </button>
        )}
      </div>

      {/* Speed controls */}
      {(isPlaying || isPaused) && (
        <div className="flex items-center gap-1 mt-3">
          <span className="text-[10px] text-zinc-500 mr-1">{t("game.speed")}:</span>
          {([1, 2, 4] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              className={`px-2.5 py-1 rounded text-xs font-mono transition-colors ${
                speed === s
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-zinc-800 text-zinc-500 hover:text-zinc-300"
              }`}
            >
              {s}x
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
