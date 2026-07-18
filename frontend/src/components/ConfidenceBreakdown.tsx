import { m } from "framer-motion";
import { useI18n } from "../i18n/LanguageContext";

/** Display order + colour per signal key; label and plain-words description come from
 *  the i18n dictionary (breakdown.<key>.label / .desc). */
const SIGNAL_COLORS: Record<string, string> = {
  llm: "var(--color-violet-soft)",
  rerank: "var(--color-amber)",
  retrieval: "#67d4e0",
  feedback: "#7ce08a",
  ai_knowledge: "var(--color-amber)",
};
const NEGATIVE_COLOR = "#e07c7c";

interface Props {
  breakdown: Record<string, number>;
  /** The AI's own sentence on why it is this confident — replaces the static
   *  ai_knowledge explanation when present. */
  note?: string | null;
}

/** WHY the confidence is what it is: one concentric ring per signal, drawn to its
 *  contribution (percentage points of the final number), each explained in plain
 *  words. Expanded from the hero's ConfidenceDial. */
export default function ConfidenceBreakdown({ breakdown, note }: Props) {
  const { t } = useI18n();
  const entries = Object.keys(SIGNAL_COLORS)
    .filter((k) => breakdown[k] !== undefined)
    .map((k) => ({
      key: k,
      value: breakdown[k],
      color: SIGNAL_COLORS[k],
      label: t(`breakdown.${k}.label`),
      // The AI's own explanation beats the canned one when it gave us one.
      desc: k === "ai_knowledge" && note ? note : t(`breakdown.${k}.desc`),
    }));
  if (entries.length === 0) return null;

  const total = Math.round(entries.reduce((s, e) => s + e.value, 0));
  const size = 116;
  const c = size / 2;

  return (
    <div className="mt-3 rounded-xl border border-glass-line bg-white/[0.03] p-3.5">
      <p className="mb-3 text-[0.82rem] text-muted">
        {entries.length > 1
          ? t("breakdown.sumMany", { total, n: entries.length })
          : t("breakdown.sumOne", { total })}
      </p>

      <div className="flex items-center gap-4">
        <svg
          viewBox={`0 0 ${size} ${size}`}
          width={size}
          height={size}
          className="shrink-0"
          aria-hidden="true"
        >
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

        <dl className="min-w-0 flex-1 space-y-2.5">
          {entries.map((e, i) => {
            const negative = e.value < 0;
            const color = negative ? NEGATIVE_COLOR : e.color;
            return (
              <m.div
                key={e.key}
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.35, delay: 0.12 * i + 0.15 }}
              >
                <dt className="flex items-baseline justify-between gap-3">
                  <span className="flex items-center gap-2 text-[0.84rem] font-medium text-ink">
                    <span
                      className="h-2 w-2 shrink-0 rounded-full"
                      style={{ background: color }}
                      aria-hidden="true"
                    />
                    {e.label}
                  </span>
                  <span className="font-mono text-[0.84rem] font-semibold" style={{ color }}>
                    {negative ? "−" : "+"}
                    {Math.abs(e.value).toFixed(1)}
                  </span>
                </dt>
                <dd className="mt-0.5 pl-4 text-[0.76rem] leading-[1.45] text-faint">{e.desc}</dd>
              </m.div>
            );
          })}
        </dl>
      </div>
    </div>
  );
}
