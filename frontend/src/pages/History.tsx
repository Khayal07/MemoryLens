import { useQuery } from "@tanstack/react-query";
import { m } from "framer-motion";
import { Link } from "react-router-dom";
import Eyebrow from "../components/ui/Eyebrow";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { developIn, fadeUp, stagger } from "../components/motion/variants";
import { api } from "../lib/api";

export default function History() {
  const { data, isLoading, isError } = useQuery({ queryKey: ["history"], queryFn: api.history });

  return (
    <div>
      <m.section variants={stagger(0.08)} initial="hidden" animate="show" className="mb-7">
        <m.div variants={developIn}>
          <Eyebrow>Your searches</Eyebrow>
        </m.div>
        <m.h1
          variants={developIn}
          className="mt-2 font-display text-[2rem] font-bold tracking-[-0.02em]"
        >
          What you've looked for
        </m.h1>
      </m.section>

      {isLoading && (
        <div className="flex flex-col gap-2.5">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[62px]" />
          ))}
        </div>
      )}

      {isError && <EmptyState title="Couldn't load your history." />}

      {data && data.length === 0 && (
        <EmptyState
          title="No searches yet."
          action={
            <Link to="/" className="text-[0.9rem] text-violet-soft hover:underline">
              Start recalling →
            </Link>
          }
        />
      )}

      {data && data.length > 0 && (
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
              <span className="font-mono text-[0.74rem] text-faint">{h.result_count} results</span>
            </m.div>
          ))}
        </m.div>
      )}
    </div>
  );
}
