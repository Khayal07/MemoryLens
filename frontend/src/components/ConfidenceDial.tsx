/** Confidence as an aperture dial: a ring that closes toward focus as certainty
 *  rises, colour shifting cold → warm amber. Used only on the hero (best) card. */
export default function ConfidenceDial({ value }: { value: number }) {
  const pct = Math.max(0, Math.min(100, Math.round(value)));
  const color =
    pct >= 75 ? "var(--amber)" : pct >= 45 ? "var(--violet-soft)" : "var(--faint)";
  const label = pct >= 75 ? "in focus" : pct >= 45 ? "coming into focus" : "still fuzzy";

  const r = 52;
  const c = 2 * Math.PI * r;
  const dash = (pct / 100) * c;

  return (
    <div
      className="dial"
      role="meter"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Confidence ${pct} percent`}
    >
      <svg viewBox="0 0 120 120" width="120" height="120">
        <circle className="dial-track" cx="60" cy="60" r={r} />
        <circle
          className="dial-fill"
          cx="60"
          cy="60"
          r={r}
          stroke={color}
          strokeDasharray={`${dash} ${c}`}
          transform="rotate(-90 60 60)"
        />
      </svg>
      <div className="dial-center">
        <span className="dial-pct" style={{ color }}>
          {pct}%
        </span>
        <span className="dial-label">{label}</span>
      </div>
    </div>
  );
}
