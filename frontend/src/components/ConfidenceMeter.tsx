/** Confidence as a "focus meter": the fill widens with certainty and shifts from
 *  cold (still fuzzy) toward warm amber (in focus) — color encodes the number. */
export default function ConfidenceMeter({ value }: { value: number }) {
  const pct = Math.round(value);
  const color =
    pct >= 75 ? "var(--amber)" : pct >= 45 ? "var(--violet-soft)" : "var(--faint)";
  return (
    <div
      className="focus"
      role="meter"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Confidence ${pct} percent`}
    >
      <div className="focus-track">
        <div className="focus-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="focus-pct" style={{ color }}>
        {pct}%
      </span>
    </div>
  );
}
