import type { CSSProperties } from "react";

const clientTiles = Array.from({ length: 16 }, (_, index) => ({
  column: index % 4,
  row: Math.floor(index / 4),
  index,
}));

export default function ClientMotionWall() {
  return (
    <div className="client-motion-wall" aria-label="Florida clients celebrating homeownership">
      <div className="client-motion-grid" aria-hidden="true">
        {clientTiles.map((tile) => (
          <div
            className={`client-motion-tile tile-drift-${tile.index % 4}`}
            key={tile.index}
            style={{
              animationDelay: `${tile.index * -0.43}s`,
            } as CSSProperties}
          >
            <span
              style={{
                backgroundPosition: `${tile.column * 33.333}% ${tile.row * 33.333}%`,
              }}
            />
          </div>
        ))}
      </div>
      <div className="client-motion-ledger" aria-hidden="true">
        <span>Real people</span>
        <span>Real keys</span>
        <span>Across Florida</span>
      </div>
    </div>
  );
}
