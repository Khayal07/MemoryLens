import { m } from "framer-motion";
import { useState } from "react";
import { useI18n } from "../i18n/LanguageContext";

/** Akinator mode: when the search comes back weak, the AI's single clarifying
 *  question rises from the console as an amber glass bubble with an inline answer
 *  field. Answering triggers a refined re-search (handled by the parent). */
export default function ClarifyBubble({
  question,
  onAnswer,
  disabled,
}: {
  question: string;
  onAnswer: (answer: string) => void;
  disabled?: boolean;
}) {
  const { t } = useI18n();
  const [answer, setAnswer] = useState("");

  function submit() {
    const a = answer.trim();
    if (!a || disabled) return;
    onAnswer(a);
    setAnswer("");
  }

  return (
    <m.div
      initial={{ opacity: 0, y: 16, scale: 0.97, filter: "blur(8px)" }}
      animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
      exit={{ opacity: 0, y: -8, filter: "blur(6px)", transition: { duration: 0.2 } }}
      transition={{ duration: 0.45, ease: [0.2, 0.7, 0.2, 1] }}
      className="glass-strong mt-5 rounded-2xl border-amber/40 p-4 shadow-glow-amber ring-1 ring-amber/30"
    >
      <div className="flex items-start gap-3">
        <span
          aria-hidden="true"
          className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full
            border border-amber/50 bg-amber/15 text-[0.95rem]"
        >
          🔮
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-[0.78rem] font-semibold uppercase tracking-[0.08em] text-amber">
            {t("clarify.oneMore")}
          </p>
          <p className="mt-1 text-[1.02rem] leading-snug text-ink">{question}</p>
          <form
            className="mt-3 flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              submit();
            }}
          >
            <input
              autoFocus
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder={t("clarify.answerPlaceholder")}
              aria-label={t("clarify.answerAria")}
              className="min-w-0 flex-1 rounded-xl border border-glass-line bg-transparent px-3 py-2
                text-[0.95rem] text-ink outline-none transition-shadow placeholder:text-faint
                focus:ring-2 focus:ring-amber/40"
            />
            <button
              type="submit"
              disabled={disabled || !answer.trim()}
              className="rounded-xl border border-amber/50 bg-amber/15 px-4 py-2 text-[0.9rem]
                font-semibold text-amber transition-all hover:bg-amber/25
                disabled:cursor-not-allowed disabled:opacity-45"
            >
              {t("clarify.refine")}
            </button>
          </form>
        </div>
      </div>
    </m.div>
  );
}
