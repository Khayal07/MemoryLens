import { useQuery } from "@tanstack/react-query";
import { m } from "framer-motion";
import { useNavigate } from "react-router-dom";
import Eyebrow from "../components/ui/Eyebrow";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { developIn, spring, stagger } from "../components/motion/variants";
import { api } from "../lib/api";

const DESC: Record<string, string> = {
  movies: "A scene, a single room, a face you can't place",
  tv: "That show with the thing that happened",
  songs: "A lyric, a mood, rain on the chorus",
  books: "Dragons, a title just out of reach",
  games: "Yellow hair, a level you replayed for years",
  actors: "Always the villain, never the name",
};

export default function CategorySelect() {
  const navigate = useNavigate();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["categories"],
    queryFn: api.categories,
  });

  return (
    <div>
      <section className="relative mb-11 overflow-hidden text-center">
        {/* breathing aperture glow behind the hero */}
        <m.div
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-[-120px] -z-10 size-[520px] -translate-x-1/2
            rounded-full bg-[radial-gradient(circle,rgba(124,107,245,0.22),transparent_60%)] blur-2xl"
          animate={{ scale: [1, 1.12, 1], opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
        />
        <m.div variants={stagger(0.08)} initial="hidden" animate="show">
          <m.div variants={developIn}>
            <Eyebrow>Half-remembered? Start here</Eyebrow>
          </m.div>
          <m.h1
            variants={developIn}
            className="my-3 font-display text-[clamp(2.2rem,6vw,3.6rem)] font-bold leading-[1.04] tracking-[-0.03em]"
          >
            You almost have it.
            <br />
            <span className="bg-gradient-to-r from-violet-soft to-amber bg-clip-text text-transparent">
              Bring it into focus.
            </span>
          </m.h1>
          <m.p variants={developIn} className="mx-auto max-w-[560px] text-[1.08rem] text-muted">
            Describe the fragment you remember — we search a real catalog and surface the
            most likely match, with how sure we are and why.
          </m.p>
        </m.div>
      </section>

      {isError && (
        <EmptyState
          title="Couldn't load categories."
          hint="Is the API running? Try refreshing in a moment."
        />
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[132px]" />
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
            <m.button
              key={c.key}
              variants={developIn}
              whileHover={{ y: -3 }}
              whileTap={{ scale: 0.98 }}
              transition={spring}
              onClick={() => navigate(`/search/${c.key}`)}
              className="group relative overflow-hidden rounded-lens border border-line
                bg-gradient-to-b from-raised to-raised/40 p-[22px] text-left
                hover:border-line-strong hover:shadow-glow
                focus-visible:outline-2 focus-visible:outline-violet-soft"
            >
              <span
                aria-hidden="true"
                className="pointer-events-none absolute -right-[30%] -top-[40%] size-[180px] rounded-full
                  bg-[radial-gradient(circle,rgba(124,107,245,0.35),transparent_65%)]
                  opacity-0 transition-opacity duration-300 group-hover:opacity-100"
              />
              <span className="text-[1.8rem] leading-none" aria-hidden="true">
                {c.icon}
              </span>
              <div className="mt-3.5 font-display text-[1.15rem] font-semibold tracking-[-0.01em]">
                {c.display_name}
              </div>
              <div className="text-[0.86rem] text-muted">
                {DESC[c.key] ?? "Search this category"}
              </div>
            </m.button>
          ))}
        </m.div>
      )}
    </div>
  );
}
