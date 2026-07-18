import { useQuery } from "@tanstack/react-query";
import { m } from "framer-motion";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import MemoryLane from "../components/MemoryLane";
import Eyebrow from "../components/ui/Eyebrow";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { developIn, fadeUp, stagger } from "../components/motion/variants";
import { cn } from "../lib/cn";
import { useI18n } from "../i18n/LanguageContext";
import { api } from "../lib/api";

export default function History() {
  const { data, isLoading, isError } = useQuery({ queryKey: ["history"], queryFn: api.history });
  const navigate = useNavigate();
  const { t } = useI18n();
  const [view, setView] = useState<"lane" | "list">("lane");

  return (
    <div>
      <m.button
        type="button"
        onClick={() => navigate(-1)}
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        whileHover={{ x: -3 }}
        className="glass mb-6 inline-flex items-center gap-2 rounded-full px-4 py-2 text-[0.85rem]
          font-medium text-muted transition-colors hover:border-violet/40 hover:text-ink
          focus-visible:outline-2 focus-visible:outline-violet-soft"
        aria-label={t("common.back")}
      >
        <span aria-hidden="true">←</span> {t("common.back")}
      </m.button>

      <m.section variants={stagger(0.08)} initial="hidden" animate="show" className="mb-7">
        <m.div variants={developIn}>
          <Eyebrow>{t("history.eyebrow")}</Eyebrow>
        </m.div>
        <m.h1
          variants={developIn}
          className="mt-2 font-display text-[2rem] font-bold tracking-[-0.02em]"
        >
          {t("history.title")}
        </m.h1>

        <m.div variants={developIn} className="mt-4 flex gap-1.5" role="tablist" aria-label={t("history.viewAria")}>
          {(["lane", "list"] as const).map((v) => (
            <button
              key={v}
              type="button"
              role="tab"
              aria-selected={view === v}
              onClick={() => setView(v)}
              className={cn(
                "rounded-full px-3.5 py-1.5 text-[0.82rem] font-medium transition-colors",
                view === v
                  ? "glass border-violet/50 text-ink shadow-glow"
                  : "text-muted hover:text-ink",
              )}
            >
              {v === "lane" ? t("history.lane") : t("history.list")}
            </button>
          ))}
        </m.div>
      </m.section>

      {isLoading && (
        <div className="flex flex-col gap-2.5">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[62px]" />
          ))}
        </div>
      )}

      {isError && <EmptyState title={t("history.loadError")} />}

      {data && data.length === 0 && (
        <EmptyState
          title={t("history.emptyTitle")}
          action={
            <Link to="/" className="text-[0.9rem] text-violet-soft hover:underline">
              {t("common.startRecalling")}
            </Link>
          }
        />
      )}

      {data && data.length > 0 && view === "lane" && <MemoryLane items={data} />}

      {data && data.length > 0 && view === "list" && (
        <m.div
          className="flex flex-col gap-2.5"
          variants={stagger(0.05)}
          initial="hidden"
          animate="show"
        >
          {data.map((h) => (
            <m.div
              key={h.id}
              variants={fadeUp}
              className="glass flex items-center justify-between gap-3 rounded-xl px-4 py-3.5
                transition-colors hover:border-violet/40"
            >
              <div>
                <div className="font-medium">{h.query}</div>
                <div className="font-mono text-[0.74rem] text-faint">
                  {h.category} · {new Date(h.created_at).toLocaleDateString()}
                </div>
              </div>
              <span className="font-mono text-[0.74rem] text-faint">{t("history.results", { count: h.result_count })}</span>
            </m.div>
          ))}
        </m.div>
      )}
    </div>
  );
}
