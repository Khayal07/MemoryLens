import { useQuery } from "@tanstack/react-query";
import { m } from "framer-motion";
import type { SimilarItem } from "../lib/types";
import { api } from "../lib/api";
import { fadeUp, stagger } from "./motion/variants";
import TiltCard from "./motion/TiltCard";
import Eyebrow from "./ui/Eyebrow";
import Skeleton from "./ui/Skeleton";

interface Props {
  itemId: number;
  icon?: string | null;
}

/** "More like this" — catalog neighbours of the best grounded match. Rendered only
 *  for real catalog items (item_id > 0); free-form answers have no neighbours. */
export default function SimilarItems({ itemId, icon }: Props) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["similar", itemId],
    queryFn: () => api.similar(itemId),
    enabled: itemId > 0,
  });

  if (isError || (data && data.length === 0)) return null;

  return (
    <section className="mt-8">
      <div className="mb-4">
        <Eyebrow>More like this</Eyebrow>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-[92px]" />
          ))}
        </div>
      ) : (
        <m.div
          className="grid grid-cols-2 gap-3.5 sm:grid-cols-3"
          variants={stagger(0.05)}
          initial="hidden"
          animate="show"
        >
          {data!.map((item) => (
            <m.div key={item.item_id} variants={fadeUp} className="h-full">
              <TiltCard className="rounded-lens">
                <SimilarCard item={item} icon={icon} />
              </TiltCard>
            </m.div>
          ))}
        </m.div>
      )}
    </section>
  );
}

function SimilarCard({ item, icon }: { item: SimilarItem; icon?: string | null }) {
  const body = (
    <div className="glass flex h-full items-center gap-3 rounded-lens p-3">
      {item.image_url ? (
        <img
          src={item.image_url}
          alt=""
          loading="lazy"
          className="h-[64px] w-[46px] shrink-0 rounded-md border border-glass-line object-cover"
        />
      ) : (
        <div
          className="flex h-[64px] w-[46px] shrink-0 items-center justify-center rounded-md
            border border-glass-line bg-white/[0.03] text-[1.2rem] text-faint"
          aria-hidden="true"
        >
          {icon ?? "🎞"}
        </div>
      )}
      <div className="min-w-0">
        <div className="truncate text-[0.95rem] font-semibold tracking-[-0.01em]">
          {item.title}
        </div>
        {item.description && (
          <div className="mt-0.5 line-clamp-2 text-[0.78rem] text-muted">{item.description}</div>
        )}
      </div>
    </div>
  );

  return item.source_url ? (
    <a href={item.source_url} target="_blank" rel="noreferrer" className="block h-full">
      {body}
    </a>
  ) : (
    body
  );
}
