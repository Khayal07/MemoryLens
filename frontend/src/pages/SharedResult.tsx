import { useQuery } from "@tanstack/react-query";
import { m } from "framer-motion";
import { Link, useParams } from "react-router-dom";
import ResultCard from "../components/ResultCard";
import Eyebrow from "../components/ui/Eyebrow";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { developIn, stagger } from "../components/motion/variants";
import { api } from "../lib/api";

export default function SharedResult() {
  const { token = "" } = useParams();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["shared", token],
    queryFn: () => api.getShared(token),
    enabled: token.length > 0,
  });

  if (isLoading) {
    return (
      <div className="space-y-3.5">
        <Skeleton className="h-[214px]" />
        <Skeleton className="h-[152px] opacity-60" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <EmptyState
        title="This shared recall isn't available."
        hint="The link may be wrong or the search was removed."
        action={
          <Link to="/" className="text-[0.9rem] text-violet-soft hover:underline">
            Try MemoryLens →
          </Link>
        }
      />
    );
  }

  return (
    <div>
      <m.section variants={stagger(0.08)} initial="hidden" animate="show" className="mb-7">
        <m.div variants={developIn}>
          <Eyebrow>Shared recall</Eyebrow>
        </m.div>
        <m.h1
          variants={developIn}
          className="mt-2 font-display text-[1.7rem] font-bold tracking-[-0.02em]"
        >
          “{data.query}”
        </m.h1>
      </m.section>

      {data.results.length === 0 ? (
        <EmptyState title="No matches were found for this recall." />
      ) : (
        <>
          <div className="mb-4">
            <Eyebrow>Best match</Eyebrow>
          </div>
          <m.div variants={stagger()} initial="hidden" animate="show">
            <ResultCard result={data.results[0]} best />
          </m.div>

          {data.results.length > 1 && (
            <>
              <div className="mb-4 mt-8">
                <Eyebrow>Other possibilities</Eyebrow>
              </div>
              <m.div
                className="grid grid-cols-1 gap-3.5 sm:grid-cols-2"
                variants={stagger(0.06)}
                initial="hidden"
                animate="show"
              >
                {data.results.slice(1).map((r, i) => (
                  <ResultCard key={`${r.item_id}-${i}`} result={r} />
                ))}
              </m.div>
            </>
          )}
        </>
      )}

      <div className="mt-10 text-center">
        <Link
          to="/"
          className="glass inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-[0.9rem]
            font-medium text-muted transition-colors hover:border-violet/40 hover:text-ink"
        >
          Recall your own memory →
        </Link>
      </div>
    </div>
  );
}
