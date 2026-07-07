import { m } from "framer-motion";

/** Display order, colour, and label for each known signal key. */
const SIGNALS: Record<string, { label: string; color: string }> = {
  llm: { label: "AI judgement", color: "var(--color-violet-soft)" },
  rerank: { label: "Relevance match", color: "var(--color-amber)" },
  retrieval: { label: "Catalog retrieval", color: "#67d4e0" },
  feedback: { label: "Community votes", color: "#7ce08a" },
  ai_knowledge: { label: "AI world knowledge", color: "var(--color-amber)" },
};
const NEGATIVE_COLOR = "#e07c7c";

interface Props {
  breakdown: Record<string, number>;
}

/** WHY the confidence is what it is: one concentric ring per signal, drawn to its
 *  contribution (percentage points of the final number), with a legend beside it.
 *  Expanded from the hero's ConfidenceDial. */
export default function ConfidenceBreakdown({ breakdown }: Props) {
  const entries = Object.keys(SIGNALS)
    .filter((k) => breakdown[k] !== undefined)
    .map((k) => ({ key: k, value: breakdown[k], ...SIGNALS[k] }));
  if (entries.length === 0) return null;

  const size = 116;
  const c = size / 2;

  return (
    <div className="mt-3 flex items-center gap-4 rounded-xl border border-glass-line bg-white/[0.03] p-3.5">
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size} aria-hidden="true">
        {entries.map((e, i) => {
          const r = 50 - i * 13;
          const circ = 2 * Math.PI * r;
          const negative = e.value < 0;
          const dash = (Math.min(Math.abs(e.value), 100) / 100) * circ;
          const color = negative ? NEGATIVE_COLOR : e.color;
          return (
            <g key={e.key}>
              <circle cx={c} cy={c} r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth={7} />
              <m.circle
                cx={c}
                cy={c}
                r={r}
                fill="none"
                stroke={color}
                strokeWidth={7}
                strokeLinecap="round"
                strokeDasharray={circ}
                transform={`rotate(-90 ${c} ${c})`}
                initial={{ strokeDashoffset: circ, opacity: 0 }}
                animate={{ strokeDashoffset: circ - dash, opacity: 1 }}
                transition={{ duration: 0.7, delay: 0.12 * i, ease: [0.2, 0.7, 0.2, 1] }}
                style={{ filter: `drop-shadow(0 0 5px ${color})` }}
              />
            </g>
          );
        })}
      </svg>

      <dl className="min-w-0 flex-1 space-y-1.5">
        {entries.map((e, i) => {
          const negative = e.value < 0;
          return (
            <m.div
              key={e.key}
              className="flex items-baseline justify-between gap-3"
              initial={{ opacity: 0, x: 8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.35, delay: 0.12 * i + 0.15 }}
            >
              <dt className="flex items-center gap-2 text-[0.82rem] text-muted">
                <span
                  className="h-2 w-2 shrink-0 rounded-full"
                  style={{ background: negative ? NEGATIVE_COLOR : e.color }}
                  aria-hidden="true"
                />
                {e.label}
              </dt>
              <dd
                className="font-mono text-[0.82rem] font-semibold"
                style={{ color: negative ? NEGATIVE_COLOR : e.color }}
              >
                {negative ? "−" : "+"}
                {Math.abs(e.value).toFixed(1)}
              </dd>
            </m.div>
          );
        })}
      </dl>
    </div>
  );
}
