import { motion } from "framer-motion";

export type CharacterMood = "working" | "happy" | "stressed" | "burnout" | "departing" | "celebrating";

interface Props {
  name: string;
  mood: CharacterMood;
  skinColor?: string;
  shirtColor: string;
  direction?: "left" | "right";
  size?: number;
}

/**
 * CSS-based pixel art character (Kairosoft style).
 * 16x16 logical grid scaled up.
 */
export function PixelCharacter({
  name,
  mood,
  shirtColor,
  skinColor = "#FFCC99",
  direction = "right",
  size = 3,
}: Props) {
  const s = size; // pixel scale factor
  const flip = direction === "left" ? -1 : 1;

  // Mood-based animation
  const moodAnimation = {
    working: {
      y: [0, -1 * s, 0],
      transition: { duration: 1.5, repeat: Infinity, ease: "easeInOut" as const },
    },
    happy: {
      y: [0, -3 * s, 0],
      transition: { duration: 0.4, repeat: Infinity, ease: "easeOut" as const },
    },
    stressed: {
      x: [-1, 1, -1, 0],
      transition: { duration: 0.3, repeat: Infinity, ease: "linear" as const },
    },
    burnout: {
      rotate: [0, -5, 5, 0],
      transition: { duration: 2, repeat: Infinity, ease: "easeInOut" as const },
    },
    departing: {
      x: [0, 60],
      opacity: [1, 0],
      transition: { duration: 1.2, ease: "easeIn" as const },
    },
    celebrating: {
      y: [0, -4 * s, 0],
      rotate: [0, 10, -10, 0],
      transition: { duration: 0.5, repeat: 3, ease: "easeOut" as const },
    },
  };

  return (
    <motion.div
      className="relative flex flex-col items-center"
      animate={moodAnimation[mood]}
      style={{ transformOrigin: "bottom center" }}
    >
      {/* Character body - pixel art style */}
      <div
        style={{
          width: 12 * s,
          height: 16 * s,
          imageRendering: "pixelated",
          transform: `scaleX(${flip})`,
        }}
        className="relative"
      >
        {/* Hair */}
        <div
          className="absolute"
          style={{
            top: 0,
            left: 2 * s,
            width: 8 * s,
            height: 3 * s,
            backgroundColor: "#4A3728",
            borderRadius: `${s}px ${s}px 0 0`,
          }}
        />
        {/* Head */}
        <div
          className="absolute"
          style={{
            top: 2 * s,
            left: 3 * s,
            width: 6 * s,
            height: 5 * s,
            backgroundColor: skinColor,
          }}
        />
        {/* Eyes */}
        <div
          className="absolute"
          style={{
            top: 4 * s,
            left: 4 * s,
            width: s,
            height: s,
            backgroundColor: mood === "burnout" ? "#FF0000" : "#333",
          }}
        />
        <div
          className="absolute"
          style={{
            top: 4 * s,
            left: 7 * s,
            width: s,
            height: s,
            backgroundColor: mood === "burnout" ? "#FF0000" : "#333",
          }}
        />
        {/* Mouth */}
        <div
          className="absolute"
          style={{
            top: 6 * s,
            left: 5 * s,
            width: 2 * s,
            height: s,
            backgroundColor:
              mood === "happy" || mood === "celebrating"
                ? "#FF6666"
                : mood === "stressed" || mood === "burnout"
                  ? "#CC9966"
                  : skinColor,
            borderRadius:
              mood === "happy" || mood === "celebrating"
                ? `0 0 ${s}px ${s}px`
                : "0",
          }}
        />
        {/* Body / Shirt */}
        <div
          className="absolute"
          style={{
            top: 7 * s,
            left: 2 * s,
            width: 8 * s,
            height: 5 * s,
            backgroundColor: shirtColor,
          }}
        />
        {/* Arms */}
        <div
          className="absolute"
          style={{
            top: 8 * s,
            left: 0,
            width: 2 * s,
            height: 3 * s,
            backgroundColor: shirtColor,
          }}
        />
        <div
          className="absolute"
          style={{
            top: 8 * s,
            left: 10 * s,
            width: 2 * s,
            height: 3 * s,
            backgroundColor: shirtColor,
          }}
        />
        {/* Legs */}
        <div
          className="absolute"
          style={{
            top: 12 * s,
            left: 3 * s,
            width: 2 * s,
            height: 4 * s,
            backgroundColor: "#4466AA",
          }}
        />
        <div
          className="absolute"
          style={{
            top: 12 * s,
            left: 7 * s,
            width: 2 * s,
            height: 4 * s,
            backgroundColor: "#4466AA",
          }}
        />

        {/* Burnout sweat drops */}
        {(mood === "burnout" || mood === "stressed") && (
          <motion.div
            className="absolute"
            style={{
              top: 2 * s,
              left: 10 * s,
              width: 2 * s,
              height: 2 * s,
              backgroundColor: "#66CCFF",
              borderRadius: `0 0 ${s}px ${s}px`,
            }}
            animate={{ y: [0, 3 * s], opacity: [1, 0] }}
            transition={{ duration: 0.8, repeat: Infinity }}
          />
        )}

        {/* Happy sparkle */}
        {(mood === "happy" || mood === "celebrating") && (
          <>
            <motion.div
              className="absolute"
              style={{
                top: -s,
                left: -s,
                width: 2 * s,
                height: 2 * s,
                backgroundColor: "#FFD700",
              }}
              animate={{ scale: [0, 1, 0], rotate: [0, 45] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
            />
            <motion.div
              className="absolute"
              style={{
                top: -2 * s,
                left: 10 * s,
                width: 2 * s,
                height: 2 * s,
                backgroundColor: "#FFD700",
              }}
              animate={{ scale: [0, 1, 0], rotate: [0, 45] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: 0.3 }}
            />
          </>
        )}
      </div>

      {/* Name label */}
      <div
        className="mt-1 text-center leading-none"
        style={{ fontSize: Math.max(8, 2.5 * s), imageRendering: "auto" }}
      >
        <span className="text-zinc-300 font-medium whitespace-nowrap">
          {name.split(" ")[0]}
        </span>
      </div>
    </motion.div>
  );
}
