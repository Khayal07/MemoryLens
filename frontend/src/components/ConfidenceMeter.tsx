import { m } from "framer-motion";
import { useI18n } from "../i18n/LanguageContext";

/** Confidence as a "focus meter": the fill widens with certainty and shifts from
 *  cold (still fuzzy) toward warm amber (in focus). Used on the compact cards. */
export default function ConfidenceMeter({ value }: { value: number }) {
  const { t } = useI18n();
  const pct = Math.round(value);
  const color =
    pct >= 75 ? "var(--color-amber)" : pct >= 45 ? "var(--color-violet-soft)" : "var(--color-faint)";
  return (
    <div
      className="mb-1 flex items-center gap-2.5"
      role="meter"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={t("confidence.ariaValue", { pct })}
    >
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.08]">
        <m.div
          className="h-full rounded-full"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: [0.2, 0.7, 0.2, 1] }}
        />
      </div>
      <span className="min-w-[48px] text-right font-mono text-[0.8rem] font-bold" style={{ color }}>
        {pct}%
      </span>
    </div>
  );
}
