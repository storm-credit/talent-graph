interface Props {
  size?: number;
}

/** Simple pixel art desk */
export function PixelDesk({ size = 3 }: Props) {
  const s = size;

  return (
    <div
      className="relative"
      style={{
        width: 16 * s,
        height: 8 * s,
        imageRendering: "pixelated",
      }}
    >
      {/* Desktop surface */}
      <div
        className="absolute"
        style={{
          top: 0,
          left: 0,
          width: 16 * s,
          height: 3 * s,
          backgroundColor: "#8B6914",
          borderRadius: `${s}px ${s}px 0 0`,
        }}
      />
      {/* Desk front panel */}
      <div
        className="absolute"
        style={{
          top: 3 * s,
          left: s,
          width: 14 * s,
          height: 5 * s,
          backgroundColor: "#A0782C",
        }}
      />
      {/* Left leg */}
      <div
        className="absolute"
        style={{
          top: 3 * s,
          left: 0,
          width: 2 * s,
          height: 5 * s,
          backgroundColor: "#6B4F1D",
        }}
      />
      {/* Right leg */}
      <div
        className="absolute"
        style={{
          top: 3 * s,
          left: 14 * s,
          width: 2 * s,
          height: 5 * s,
          backgroundColor: "#6B4F1D",
        }}
      />
      {/* Monitor */}
      <div
        className="absolute"
        style={{
          top: -4 * s,
          left: 5 * s,
          width: 6 * s,
          height: 4 * s,
          backgroundColor: "#333",
          border: `${Math.max(1, s * 0.5)}px solid #555`,
        }}
      />
      {/* Screen glow */}
      <div
        className="absolute"
        style={{
          top: -3.5 * s,
          left: 5.5 * s,
          width: 5 * s,
          height: 3 * s,
          backgroundColor: "#4488CC",
        }}
      />
    </div>
  );
}
