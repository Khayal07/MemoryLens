import { useQuery } from "@tanstack/react-query";
import { m } from "framer-motion";
import { useNavigate } from "react-router-dom";
import Eyebrow from "../components/ui/Eyebrow";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import TiltCard from "../components/motion/TiltCard";
import { developIn, stagger } from "../components/motion/variants";
import { categoryName, useI18n } from "../i18n/LanguageContext";
import { api } from "../lib/api";

export default function CategorySelect() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["categories"],
    queryFn: api.categories,
  });

  return (
    <div>
      <section className="relative mb-14 pt-6 text-center">
        <m.div variants={stagger(0.08)} initial="hidden" animate="show">
          <m.div variants={developIn}>
            <Eyebrow>{t("category.eyebrow")}</Eyebrow>
          </m.div>
          <m.h1
            variants={developIn}
            className="my-4 font-display text-[clamp(2.6rem,7vw,4.6rem)] font-bold leading-[1.02] tracking-[-0.035em]"
          >
            {t("category.title1")}
            <br />
            <span className="bg-gradient-to-r from-violet-soft via-violet to-amber bg-clip-text text-transparent [text-shadow:0_0_40px_rgba(124,107,245,0.25)]">
              {t("category.title2")}
            </span>
          </m.h1>
          <m.p variants={developIn} className="mx-auto max-w-[580px] text-[1.12rem] text-muted">
            {t("category.subtitle")}
          </m.p>
        </m.div>
      </section>

      {isError && (
        <EmptyState title={t("category.errorTitle")} hint={t("category.errorHint")} />
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[148px]" />
          ))}
        </div>
      ) : (
        <m.div
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
          variants={stagger(0.06)}
          initial="hidden"
          animate="show"
        >
          {data?.map((c) => (
            <m.div key={c.key} variants={developIn}>
              <TiltCard className="rounded-lens">
                <button
                  onClick={() => navigate(`/search/${c.key}`)}
                  className="glass group flex h-full w-full flex-col rounded-lens p-[22px] text-left
                    transition-[border-color,box-shadow] hover:border-violet/50
                    focus-visible:outline-2 focus-visible:outline-violet-soft"
                >
                  <span
                    className="mb-4 inline-flex size-11 items-center justify-center rounded-xl border border-glass-line
                      bg-violet/10 text-[1.5rem] shadow-[0_0_20px_-4px_rgba(124,107,245,0.5)]
                      transition-shadow group-hover:shadow-[0_0_28px_-2px_rgba(124,107,245,0.8)]"
                    aria-hidden="true"
                  >
                    {c.icon}
                  </span>
                  <div className="font-display text-[1.2rem] font-semibold tracking-[-0.01em]">
                    {categoryName(t, c.key, c.display_name)}
                  </div>
                  <div className="mt-1 text-[0.88rem] text-muted">
                    {t(`category.desc.${c.key}`) || t("category.searchThis")}
                  </div>
                </button>
              </TiltCard>
            </m.div>
          ))}
        </m.div>
      )}
    </div>
  );
}
