import { useQuery } from "@tanstack/react-query";
import { m } from "framer-motion";
import { useRef } from "react";
import { useNavigate } from "react-router-dom";
import type { SearchSummary } from "../lib/types";
import { useI18n } from "../i18n/LanguageContext";
import { api } from "../lib/api";
import PosterPlaceholder from "./PosterPlaceholder";

interface Props {
  items: SearchSummary[];
}

function dayLabel(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

/** Memory Lane — the search history as a horizontal, scroll-snapping film strip:
 *  one glass card per search with its best-match poster, day markers where the
 *  date changes, cards revealing as they scroll into the lane. */
export default function MemoryLane({ items }: Props) {
  const { t } = useI18n();
  const laneRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { data: categories } = useQuery({ queryKey: ["categories"], queryFn: api.categories });
  const iconOf = (key: string) => categories?.find((c) => c.key === key)?.icon ?? "🔎";

  return (
    <div
      ref={laneRef}
      className="flex snap-x snap-mandatory gap-4 overflow-x-auto pb-5 pt-1
        [scrollbar-color:rgba(124,107,245,0.35)_transparent] [scrollbar-width:thin]"
      role="list"
      aria-label={t("history.timelineAria")}
    >
      {items.map((h, i) => {
        const newDay = i === 0 || dayLabel(items[i - 1].created_at) !== dayLabel(h.created_at);
        return (
          <div key={h.id} role="listitem" className="flex shrink-0 snap-start items-stretch gap-4">
            {newDay && (
              <div className="flex flex-col items-center justify-center gap-2 px-1" aria-hidden="true">
                <span className="h-full w-px bg-gradient-to-b from-transparent via-violet/40 to-transparent" />
                <span className="whitespace-nowrap font-mono text-[0.7rem] tracking-[0.08em] text-faint [writing-mode:vertical-rl]">
                  {dayLabel(h.created_at)}
                </span>
                <span className="h-full w-px bg-gradient-to-b from-transparent via-violet/40 to-transparent" />
              </div>
            )}

            <m.button
              type="button"
              onClick={() => navigate(`/search/${h.category}`)}
              initial={{ opacity: 0, y: 18, scale: 0.97 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              viewport={{ root: laneRef, amount: 0.35, once: true }}
              whileHover={{ y: -4 }}
              transition={{ duration: 0.45, ease: [0.2, 0.7, 0.2, 1] }}
              className="glass w-[200px] rounded-lens p-3 text-left transition-colors hover:border-violet/50"
              aria-label={t("history.bestAria", {
                query: h.query,
                title: h.top_title ?? t("history.unknown"),
              })}
            >
              <div className="relative overflow-hidden rounded-[10px]">
                {h.top_image ? (
                  <img
                    src={h.top_image}
                    alt=""
                    loading="lazy"
                    className="h-[250px] w-full object-cover"
                  />
                ) : (
                  <PosterPlaceholder posterSize="h-[250px] w-full" icon={iconOf(h.category)} />
                )}
                {h.top_confidence != null && (
                  <span className="absolute right-2 top-2 rounded-full bg-black/55 px-2 py-0.5 font-mono text-[0.72rem] font-semibold text-amber backdrop-blur-sm">
                    {Math.round(h.top_confidence)}%
                  </span>
                )}
              </div>

              {h.top_title && (
                <div className="mt-2.5 truncate font-display text-[0.98rem] font-semibold">
                  {h.top_title}
                </div>
              )}
              <p className="mt-1 line-clamp-2 text-[0.8rem] leading-[1.4] text-muted">
                “{h.query}”
              </p>
              <div className="mt-2 flex items-center gap-1.5 font-mono text-[0.7rem] text-faint">
                <span aria-hidden="true">{iconOf(h.category)}</span>
                {h.category}
                <span className="ml-auto">
                  {new Date(h.created_at).toLocaleTimeString(undefined, {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
            </m.button>
          </div>
        );
      })}
    </div>
  );
}
