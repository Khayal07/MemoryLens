import { m, AnimatePresence } from "framer-motion";
import { useI18n } from "../i18n/LanguageContext";
import { cn } from "../lib/cn";

interface Props {
  fragments: string[];
  onChange: (fragments: string[]) => void;
  draft: string;
  onDraftChange: (draft: string) => void;
  /** While the search runs, chips get "pulled into the lens" (toward Recall). */
  isPending: boolean;
  placeholder?: string;
}

const chipVariants = {
  rest: (i: number) => ({
    x: 0,
    opacity: 1,
    scale: 1,
    transition: { delay: i * 0.03, type: "spring" as const, stiffness: 320, damping: 26 },
  }),
  fly: (i: number) => ({
    x: 70,
    opacity: 0.25,
    scale: 0.85,
    transition: { delay: i * 0.06, duration: 0.4, ease: "easeIn" as const },
  }),
};

/** Multi-fragment recall: each half-memory ("qırmızı həb", "yavaş güllə") becomes a
 *  glass chip; Enter adds the next one, Backspace on an empty input removes the last,
 *  and Recall searches them all as one combined memory. */
export default function FragmentBoard({
  fragments,
  onChange,
  draft,
  onDraftChange,
  isPending,
  placeholder,
}: Props) {
  const { t } = useI18n();
  function addDraft() {
    const f = draft.trim();
    if (!f) return;
    if (!fragments.includes(f)) onChange([...fragments, f]);
    onDraftChange("");
  }

  return (
    <div className="flex min-h-[52px] flex-1 flex-wrap items-center gap-2 px-3 py-2">
      <AnimatePresence initial={false}>
        {fragments.map((f, i) => (
          <m.span
            key={f}
            layout
            custom={i}
            variants={chipVariants}
            initial={{ opacity: 0, scale: 0.7, y: 6 }}
            animate={isPending ? "fly" : "rest"}
            exit={{ opacity: 0, scale: 0.7, transition: { duration: 0.15 } }}
            className="glass inline-flex items-center gap-1.5 rounded-full border-violet/30 py-1 pl-3 pr-1.5 text-[0.88rem] text-ink"
          >
            {f}
            <button
              type="button"
              onClick={() => onChange(fragments.filter((x) => x !== f))}
              aria-label={t("fragment.removeAria", { f })}
              className="flex h-5 w-5 items-center justify-center rounded-full text-faint transition-colors hover:bg-white/10 hover:text-ink"
            >
              ✕
            </button>
          </m.span>
        ))}
      </AnimatePresence>

      <input
        autoFocus
        value={draft}
        onChange={(e) => onDraftChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && draft.trim()) {
            // Non-empty draft: Enter banks the chip; a second Enter (empty) submits.
            e.preventDefault();
            addDraft();
          } else if (e.key === "Backspace" && !draft && fragments.length > 0) {
            onChange(fragments.slice(0, -1));
          }
        }}
        onBlur={addDraft}
        placeholder={fragments.length === 0 ? placeholder : t("fragment.addAnother")}
        aria-label={t("fragment.addAria")}
        className={cn(
          "min-w-[140px] flex-1 bg-transparent px-1 py-2 text-[1.05rem] leading-[1.45]",
          "text-ink outline-none placeholder:text-faint",
        )}
      />
    </div>
  );
}
