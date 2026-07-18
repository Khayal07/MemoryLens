import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, m } from "framer-motion";
import { useState } from "react";
import Alert from "../components/ui/Alert";
import Button from "../components/ui/Button";
import Eyebrow from "../components/ui/Eyebrow";
import Skeleton from "../components/ui/Skeleton";
import { photoDevelop, stagger } from "../components/motion/variants";
import { useI18n } from "../i18n/LanguageContext";
import { api, ApiError } from "../lib/api";
import type { ChallengeState } from "../lib/types";

/** A clue card flips in like a card turning face-up. */
const flipIn = {
  hidden: { opacity: 0, rotateY: -90 },
  show: {
    opacity: 1,
    rotateY: 0,
    transition: { duration: 0.55, ease: [0.2, 0.7, 0.2, 1] as const },
  },
};

function emojiGrid(s: ChallengeState): string {
  const wrong = "🟨".repeat(Math.max(0, s.guesses_used - (s.solved ? 1 : 0)));
  const tail = s.solved ? "🟩" : "🟥";
  const score = s.solved ? `${s.guesses_used}/${s.guess_limit}` : `X/${s.guess_limit}`;
  return `🔍${wrong}${tail} MemoryLens #${s.number} ${score}`;
}

export default function Challenge() {
  const qc = useQueryClient();
  const { t } = useI18n();
  const { data, isLoading, error } = useQuery({
    queryKey: ["challenge"],
    queryFn: api.challengeToday,
  });
  const [guess, setGuess] = useState("");
  // Bumped on every wrong guess so the input re-runs its shake keyframes.
  const [shakeKey, setShakeKey] = useState(0);
  const [copied, setCopied] = useState(false);

  const mutation = useMutation({
    mutationFn: (g: string) => api.challengeGuess(g),
    onSuccess: (s) => {
      qc.setQueryData(["challenge"], s);
      if (s.correct === false) setShakeKey((k) => k + 1);
      setGuess("");
    },
  });

  function submit() {
    const g = guess.trim();
    if (!g || mutation.isPending) return;
    mutation.mutate(g);
  }

  async function share(s: ChallengeState) {
    await navigator.clipboard.writeText(emojiGrid(s));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (isLoading) {
    return (
      <div className="space-y-3.5">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-[120px]" />
        <Skeleton className="h-[56px]" />
      </div>
    );
  }
  if (error || !data) {
    return <Alert>{(error as ApiError | null)?.message ?? t("challenge.unavailable")}</Alert>;
  }

  const lockedCount = data.clues_total - data.clues.length;

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3">
        <Eyebrow>{t("challenge.daily", { n: data.number })}</Eyebrow>
        <span className="glass rounded-full px-3 py-1.5 text-[0.82rem] text-muted">
          {t("challenge.category")} <span className="text-ink">{data.category}</span>
        </span>
      </div>
      <h1 className="mb-6 font-display text-[1.5rem] font-bold tracking-[-0.02em]">
        {t("challenge.title")}
      </h1>

      <m.div
        className="space-y-3 [perspective:1200px]"
        variants={stagger(0.12)}
        initial="hidden"
        animate="show"
      >
        {data.clues.map((clue, i) => (
          <m.div
            key={clue}
            variants={flipIn}
            className="glass rounded-2xl p-4 [transform-style:preserve-3d]"
          >
            <span className="mr-3 inline-flex h-7 w-7 items-center justify-center rounded-full
              border border-violet/50 bg-violet/15 text-[0.8rem] font-bold text-violet-soft">
              {i + 1}
            </span>
            <span className="text-[1rem] leading-relaxed">{clue}</span>
          </m.div>
        ))}
        {Array.from({ length: lockedCount }).map((_, i) => (
          <div
            key={`locked-${i}`}
            className="glass flex items-center gap-3 rounded-2xl p-4 opacity-45"
            aria-label={t("challenge.lockedAria")}
          >
            <span className="inline-flex h-7 w-7 items-center justify-center rounded-full
              border border-glass-line text-[0.8rem]">
              🔒
            </span>
            <span className="text-[0.9rem] text-faint">
              {t("challenge.locked")}
            </span>
          </div>
        ))}
      </m.div>

      {!data.finished && (
        <m.form
          key={shakeKey}
          animate={shakeKey ? { x: [0, -12, 12, -7, 7, 0] } : undefined}
          transition={{ duration: 0.4 }}
          className="glass-strong mt-6 flex gap-2.5 rounded-2xl p-2.5 transition-shadow
            focus-within:shadow-glow focus-within:ring-2 focus-within:ring-violet/50"
          onSubmit={(e) => {
            e.preventDefault();
            submit();
          }}
        >
          <input
            autoFocus
            value={guess}
            onChange={(e) => setGuess(e.target.value)}
            placeholder={t("challenge.guessPlaceholder", { category: data.category })}
            aria-label={t("challenge.guessAria")}
            className="min-w-0 flex-1 bg-transparent px-3 py-3 text-[1.05rem] text-ink
              outline-none placeholder:text-faint"
          />
          <Button type="submit" disabled={mutation.isPending || !guess.trim()}>
            {mutation.isPending
              ? t("challenge.checking")
              : t("challenge.guessN", { n: data.guesses_used + 1, limit: data.guess_limit })}
          </Button>
        </m.form>
      )}

      <AnimatePresence>
        {data.correct === false && !data.finished && (
          <m.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-3 text-[0.92rem] text-amber"
          >
            {t("challenge.notIt")}
          </m.p>
        )}
      </AnimatePresence>

      {data.finished && data.answer && (
        <m.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.2, 0.7, 0.2, 1] }}
          className={`glass-strong mt-8 overflow-hidden rounded-3xl p-5 ring-1 ${
            data.solved ? "ring-violet/40 shadow-glow" : "ring-amber/40 shadow-glow-amber"
          }`}
        >
          <Eyebrow>{data.solved ? t("challenge.solvedIn", { n: data.guesses_used, limit: data.guess_limit }) : t("challenge.outOfGuesses")}</Eyebrow>
          <div className="mt-4 flex flex-col gap-5 sm:flex-row">
            {data.answer.image_url && (
              <m.img
                src={data.answer.image_url}
                alt={data.answer.title}
                variants={photoDevelop}
                initial="hidden"
                animate="show"
                className="h-52 w-36 shrink-0 rounded-xl object-cover"
              />
            )}
            <div className="min-w-0">
              <h2 className="font-display text-[1.6rem] font-bold tracking-[-0.02em]">
                {data.answer.title}
              </h2>
              <p className="mt-2 text-[0.95rem] text-muted">
                {data.solved ? t("challenge.solvedMsg") : t("challenge.failedMsg")}
              </p>
              <div className="mt-4 flex flex-wrap items-center gap-2.5">
                <button
                  onClick={() => share(data)}
                  className="glass rounded-full px-4 py-2 text-[0.9rem] font-semibold
                    transition-colors hover:border-violet/60"
                >
                  {copied ? t("challenge.copied") : t("challenge.shareResult")}
                </button>
                <span className="text-[0.95rem]">{emojiGrid(data)}</span>
                {data.answer.source_url && (
                  <a
                    href={data.answer.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[0.9rem] text-violet-soft underline-offset-4 hover:underline"
                  >
                    {t("common.viewSource")}
                  </a>
                )}
              </div>
            </div>
          </div>
        </m.div>
      )}
    </div>
  );
}
