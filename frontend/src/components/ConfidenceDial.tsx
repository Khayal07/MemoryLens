import { animate, m, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";
import { useI18n } from "../i18n/LanguageContext";

/** Confidence as an aperture dial: a ring that fills toward focus as certainty
 *  rises, colour shifting cold → warm amber, with a spring count-up. Hero only. */
export default function ConfidenceDial({ value }: { value: number }) {
  const { t } = useI18n();
  const pct = Math.max(0, Math.min(100, Math.round(value)));
  const reduce = useReducedMotion();
  const [shown, setShown] = useState(reduce ? pct : 0);

  const color =
    pct >= 75 ? "var(--color-amber)" : pct >= 45 ? "var(--color-violet-soft)" : "var(--color-faint)";
  const label =
    pct >= 75 ? t("confidence.inFocus") : pct >= 45 ? t("confidence.coming") : t("confidence.fuzzy");

  const r = 52;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;

  useEffect(() => {
    if (reduce) {
      setShown(pct);
      return;
    }
    const controls = animate(0, pct, {
      duration: 0.9,
      ease: [0.2, 0.7, 0.2, 1],
      onUpdate: (v) => setShown(Math.round(v)),
    });
    return () => controls.stop();
  }, [pct, reduce]);

  return (
    <div
      className="relative size-[120px]"
      role="meter"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={t("confidence.ariaValue", { pct })}
    >
      <svg viewBox="0 0 120 120" width="120" height="120" style={{ filter: `drop-shadow(0 0 8px ${color})` }}>
        <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={8} />
        <m.circle
          cx="60"
          cy="60"
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeLinecap="round"
          strokeDasharray={circ}
          transform="rotate(-90 60 60)"
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ - dash }}
          transition={{ duration: 0.9, ease: [0.2, 0.7, 0.2, 1] }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-0.5">
        <span className="font-mono text-[1.4rem] font-bold leading-none" style={{ color }}>
          {shown}%
        </span>
        <span className="text-[0.66rem] tracking-[0.04em] text-faint">{label}</span>
      </div>
    </div>
  );
}
