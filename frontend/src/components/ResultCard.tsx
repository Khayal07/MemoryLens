import { AnimatePresence, m } from "framer-motion";
import { useState } from "react";
import type { ResultItem } from "../lib/types";
import { cn } from "../lib/cn";
import { apertureBloom, developIn, photoDevelop, photoDevelopSoft } from "./motion/variants";
import TiltCard from "./motion/TiltCard";
import Badge from "./ui/Badge";
import ConfidenceBreakdown from "./ConfidenceBreakdown";
import ConfidenceDial from "./ConfidenceDial";
import ConfidenceMeter from "./ConfidenceMeter";
import SaveButton from "./SaveButton";
import FeedbackButtons from "./FeedbackButtons";
import PosterPlaceholder from "./PosterPlaceholder";

interface Props {
  result: ResultItem;
  best?: boolean;
  icon?: string | null;
  searchId?: number;
}

/** Internal metadata keys that should never be shown as user-facing tags. */
const HIDDEN_META = new Set(["source", "image_url", "source_url"]);

export default function ResultCard({ result, best, icon, searchId }: Props) {
  const [imageFailed, setImageFailed] = useState(false);
  // The darkroom develop only starts once the poster has actually loaded, so the
  // blur→sharp reveal never plays over an empty frame.
  const [imageLoaded, setImageLoaded] = useState(false);
  const [showBreakdown, setShowBreakdown] = useState(false);
  const breakdown = result.breakdown ?? null;
  const byAI = result.metadata?.source === "gpt-knowledge";
  // Show any real poster we have — including an OMDb one fetched for the AI hero.
  const showImage = result.image_url && !imageFailed;

  const tags = Object.entries(result.metadata)
    .filter(([k, v]) => !HIDDEN_META.has(k) && v !== null && v !== undefined && v !== "")
    .slice(0, 4);

  const posterSize = best ? "w-[148px] h-[214px]" : "w-[84px] h-[120px]";

  const body = (
    <article
      className={cn(
        "relative grid h-full rounded-lens",
        best
          ? "glass-strong grid-cols-[148px_1fr] items-center gap-6 p-[26px] max-sm:grid-cols-1 max-sm:justify-items-center max-sm:text-center"
          : "glass grid-cols-[84px_1fr] gap-4 p-4",
        best &&
          (byAI
            ? "shadow-glow-amber ring-1 ring-amber/30 border-amber/40"
            : "shadow-glow ring-1 ring-violet/30 border-violet/40"),
      )}
    >
      {/* Free-form AI answers are materialized as real catalog rows, so they carry a
          real item_id and can be saved too; SaveButton self-hides when item_id <= 0. */}
      <div className="absolute right-3 top-3 z-30">
        <SaveButton itemId={result.item_id} />
      </div>
      {showImage ? (
        // overflow-hidden keeps the heavy develop blur from bleeding past the corners.
        <div className={cn("overflow-hidden rounded-[10px] border border-glass-line", posterSize)}>
          <m.img
            className="h-full w-full object-cover"
            src={result.image_url!}
            alt=""
            loading="lazy"
            variants={best ? photoDevelop : photoDevelopSoft}
            initial="hidden"
            animate={imageLoaded ? "show" : "hidden"}
            onLoad={() => setImageLoaded(true)}
            ref={(el: HTMLImageElement | null) => {
              // Cached images can be complete before onLoad ever fires.
              if (el?.complete) setImageLoaded(true);
            }}
            onError={() => setImageFailed(true)}
          />
        </div>
      ) : (
        <m.div variants={best ? apertureBloom : undefined}>
          <PosterPlaceholder
            posterSize={posterSize}
            tone={byAI ? "amber" : "violet"}
            icon={icon}
            big={best}
          />
        </m.div>
      )}

      <div className="min-w-0">
        {byAI && (
          <Badge tone="amber" className="mb-3">
            ✦ AI knowledge
          </Badge>
        )}

        {best ? (
          breakdown ? (
            <div>
              <button
                type="button"
                onClick={() => setShowBreakdown((v) => !v)}
                aria-expanded={showBreakdown}
                aria-label="Why this confidence? Toggle the signal breakdown"
                className="group rounded-full text-left outline-none focus-visible:ring-2 focus-visible:ring-violet/60"
              >
                <ConfidenceDial value={result.confidence} />
                <span className="mt-1 block text-center text-[0.68rem] text-faint transition-colors group-hover:text-muted">
                  why? {showBreakdown ? "▴" : "▾"}
                </span>
              </button>
              <AnimatePresence>
                {showBreakdown && (
                  <m.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3, ease: [0.2, 0.7, 0.2, 1] }}
                    className="overflow-hidden"
                  >
                    <ConfidenceBreakdown breakdown={breakdown} />
                  </m.div>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <ConfidenceDial value={result.confidence} />
          )
        ) : (
          <div className={cn(!byAI && "pr-10")}>
            <ConfidenceMeter value={result.confidence} />
          </div>
        )}

        <h3
          className={cn(
            "font-display font-semibold tracking-[-0.01em]",
            best ? "mt-3 text-[1.7rem]" : "mt-2 text-[1.1rem]",
          )}
        >
          {result.title}
        </h3>

        {result.reason && (
          <p className="my-2 text-[0.95rem] text-ink">
            <span className="mr-0.5 font-display text-violet-soft">“</span>
            {result.reason}
            <span className="ml-0.5 font-display text-violet-soft">”</span>
          </p>
        )}
        {result.description && <p className="text-[0.9rem] text-muted">{result.description}</p>}

        {tags.length > 0 && (
          <div className="mt-2.5 flex flex-wrap gap-1.5">
            {tags.map(([k, v]) => (
              <span
                key={k}
                className="rounded-md border border-glass-line bg-white/[0.03] px-1.5 py-0.5 font-mono text-[0.7rem] text-muted"
              >
                {k}: {String(Array.isArray(v) ? v.join(", ") : v)}
              </span>
            ))}
          </div>
        )}

        {result.source_url && (
          <a
            className="mt-2.5 inline-block text-[0.82rem] text-violet-soft hover:underline"
            href={result.source_url}
            target="_blank"
            rel="noreferrer"
          >
            View source ↗
          </a>
        )}

        {searchId !== undefined && (
          <FeedbackButtons searchId={searchId} itemId={result.item_id} />
        )}
      </div>
    </article>
  );

  return (
    <m.div variants={developIn} className="h-full">
      <TiltCard className="rounded-lens" max={best ? 4 : 7}>
        {body}
      </TiltCard>
    </m.div>
  );
}
