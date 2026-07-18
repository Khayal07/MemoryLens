import { useQuery } from "@tanstack/react-query";
import { m } from "framer-motion";
import { useNavigate } from "react-router-dom";
import Eyebrow from "../components/ui/Eyebrow";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { developIn, fadeUp, stagger } from "../components/motion/variants";
import { useI18n } from "../i18n/LanguageContext";
import { api } from "../lib/api";
import type { LabelCount } from "../lib/types";

export default function Analytics() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["analytics"],
    queryFn: api.analytics,
  });

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
          <Eyebrow>{t("analytics.eyebrow")}</Eyebrow>
        </m.div>
        <m.h1
          variants={developIn}
          className="mt-2 font-display text-[2rem] font-bold tracking-[-0.02em]"
        >
          {t("analytics.title")}
        </m.h1>
      </m.section>

      {isLoading && (
        <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[92px]" />
          ))}
        </div>
      )}

      {isError && <EmptyState title={t("analytics.loadError")} />}

      {data && (
        <div className="space-y-9">
          <m.div
            className="grid grid-cols-2 gap-3.5 sm:grid-cols-4"
            variants={stagger(0.06)}
            initial="hidden"
            animate="show"
          >
            <Stat label={t("analytics.total")} value={data.total_searches} />
            <Stat label={t("analytics.last7")} value={data.searches_last_7d} />
            <Stat label={t("analytics.avgConfidence")} value={`${data.avg_confidence}%`} />
            <Stat label={t("analytics.grounded")} value={`${grounded(data.grounded_searches, data.total_searches)}%`} />
          </m.div>

          <BarBlock title={t("analytics.byCategory")} rows={data.by_category} noData={t("analytics.noData")} />

          <section>
            <div className="mb-4">
              <Eyebrow>{t("analytics.feedback")}</Eyebrow>
            </div>
            <div className="grid grid-cols-2 gap-3.5">
              <Stat label={t("analytics.upvotes")} value={data.upvotes} />
              <Stat label={t("analytics.downvotes")} value={data.downvotes} />
            </div>
          </section>

          <section>
            <div className="mb-4">
              <Eyebrow>{t("analytics.topQueries")}</Eyebrow>
            </div>
            {data.top_queries.length === 0 ? (
              <p className="glass rounded-xl px-4 py-6 text-center text-[0.88rem] text-faint">
                {t("analytics.noSearches")}
              </p>
            ) : (
              <m.div
                className="flex flex-col gap-2"
                variants={stagger(0.04)}
                initial="hidden"
                animate="show"
              >
                {data.top_queries.map((q, i) => (
                  <m.div
                    key={`${q.label}-${i}`}
                    variants={fadeUp}
                    className="glass flex items-center justify-between gap-3 rounded-xl px-4 py-3"
                  >
                    <span className="truncate text-[0.92rem]">{q.label}</span>
                    <span className="shrink-0 font-mono text-[0.78rem] text-faint">
                      {q.count}×
                    </span>
                  </m.div>
                ))}
              </m.div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

function grounded(g: number, total: number): number {
  return total > 0 ? Math.round((g / total) * 100) : 0;
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <m.div variants={fadeUp} className="glass rounded-xl p-4">
      <div className="font-display text-[1.9rem] font-bold tracking-[-0.02em]">{value}</div>
      <div className="mt-0.5 text-[0.8rem] text-muted">{label}</div>
    </m.div>
  );
}

function BarBlock({ title, rows, noData }: { title: string; rows: LabelCount[]; noData: string }) {
  const max = Math.max(1, ...rows.map((r) => r.count));
  return (
    <section>
      <div className="mb-4">
        <Eyebrow>{title}</Eyebrow>
      </div>
      {rows.length === 0 ? (
        <p className="glass rounded-xl px-4 py-6 text-center text-[0.88rem] text-faint">
          {noData}
        </p>
      ) : (
        <div className="glass space-y-3 rounded-xl p-4">
          {rows.map((r) => (
            <div key={r.label}>
              <div className="mb-1 flex items-center justify-between text-[0.85rem]">
                <span className="capitalize">{r.label}</span>
                <span className="font-mono text-[0.75rem] text-faint">{r.count}</span>
              </div>
              <div className="h-2.5 overflow-hidden rounded-full bg-white/[0.05]">
                <m.div
                  className="h-full rounded-full bg-gradient-to-r from-violet-soft to-amber"
                  initial={{ width: 0 }}
                  animate={{ width: `${(r.count / max) * 100}%` }}
                  transition={{ duration: 0.6, ease: "easeOut" }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
