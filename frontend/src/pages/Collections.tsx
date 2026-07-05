import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { m } from "framer-motion";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Eyebrow from "../components/ui/Eyebrow";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { developIn, fadeUp, stagger } from "../components/motion/variants";
import TiltCard from "../components/motion/TiltCard";
import PosterPlaceholder from "../components/PosterPlaceholder";
import { api } from "../lib/api";
import type { Collection, SavedItem } from "../lib/types";

export default function Collections() {
  const qc = useQueryClient();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const { data, isLoading, isError } = useQuery({
    queryKey: ["collections"],
    queryFn: api.collections,
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ["collections"] });

  const create = useMutation({
    mutationFn: (n: string) => api.createCollection(n),
    onSuccess: () => {
      setName("");
      invalidate();
    },
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
        aria-label="Go back"
      >
        <span aria-hidden="true">←</span> Back
      </m.button>

      <m.section variants={stagger(0.08)} initial="hidden" animate="show" className="mb-7">
        <m.div variants={developIn}>
          <Eyebrow>Saved</Eyebrow>
        </m.div>
        <m.h1
          variants={developIn}
          className="mt-2 font-display text-[2rem] font-bold tracking-[-0.02em]"
        >
          Your collections
        </m.h1>
      </m.section>

      <form
        className="glass-strong mb-8 flex gap-2 rounded-xl p-2"
        onSubmit={(e) => {
          e.preventDefault();
          const n = name.trim();
          if (n) create.mutate(n);
        }}
      >
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Create a new collection…"
          maxLength={80}
          className="min-w-0 flex-1 rounded-lg bg-transparent px-3 py-2.5 text-[0.98rem] text-ink
            placeholder:text-faint focus:outline-none"
        />
        <button
          type="submit"
          disabled={!name.trim() || create.isPending}
          className="rounded-lg bg-gradient-to-r from-violet-soft to-amber px-4 py-2.5 text-[0.9rem]
            font-semibold text-[#14122b] disabled:opacity-50"
        >
          Create
        </button>
      </form>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-[120px]" />
          ))}
        </div>
      )}

      {isError && <EmptyState title="Couldn't load your collections." />}

      {data && data.length === 0 && (
        <EmptyState
          title="No collections yet."
          hint="Search, then tap ✦ on a result to save it here."
          action={
            <Link to="/" className="text-[0.9rem] text-violet-soft hover:underline">
              Start recalling →
            </Link>
          }
        />
      )}

      <div className="space-y-8">
        {data?.map((col) => (
          <CollectionSection key={col.id} collection={col} onChange={invalidate} />
        ))}
      </div>
    </div>
  );
}

function CollectionSection({
  collection,
  onChange,
}: {
  collection: Collection;
  onChange: () => void;
}) {
  const [renaming, setRenaming] = useState(false);
  const [name, setName] = useState(collection.name);

  const rename = useMutation({
    mutationFn: (n: string) => api.renameCollection(collection.id, n),
    onSuccess: () => {
      setRenaming(false);
      onChange();
    },
  });
  const remove = useMutation({
    mutationFn: () => api.deleteCollection(collection.id),
    onSuccess: onChange,
  });
  const removeItem = useMutation({
    mutationFn: (itemId: number) => api.removeFromCollection(collection.id, itemId),
    onSuccess: onChange,
  });

  return (
    <section>
      <div className="mb-3 flex items-center justify-between gap-3">
        {renaming ? (
          <form
            className="flex flex-1 gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              const n = name.trim();
              if (n) rename.mutate(n);
            }}
          >
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={80}
              className="min-w-0 flex-1 rounded-lg border border-glass-line bg-night/50 px-3 py-1.5
                text-[1rem] text-ink focus:border-violet focus:outline-none"
            />
            <button type="submit" className="text-[0.85rem] text-violet-soft hover:underline">
              Save
            </button>
            <button
              type="button"
              onClick={() => {
                setRenaming(false);
                setName(collection.name);
              }}
              className="text-[0.85rem] text-faint hover:text-muted"
            >
              Cancel
            </button>
          </form>
        ) : (
          <h2 className="font-display text-[1.3rem] font-semibold tracking-[-0.01em]">
            {collection.name}
            <span className="ml-2 font-mono text-[0.72rem] text-faint">
              {collection.items.length}
            </span>
          </h2>
        )}

        {!renaming && (
          <div className="flex shrink-0 gap-3 text-[0.82rem]">
            <button onClick={() => setRenaming(true)} className="text-muted hover:text-ink">
              Rename
            </button>
            <button
              onClick={() => remove.mutate()}
              className="text-muted hover:text-red-300"
            >
              Delete
            </button>
          </div>
        )}
      </div>

      {collection.items.length === 0 ? (
        <p className="glass rounded-xl px-4 py-6 text-center text-[0.88rem] text-faint">
          Empty — save results here with ✦.
        </p>
      ) : (
        <m.div
          className="grid grid-cols-2 gap-3.5 sm:grid-cols-3"
          variants={stagger(0.05)}
          initial="hidden"
          animate="show"
        >
          {collection.items.map((item) => (
            <m.div key={item.item_id} variants={fadeUp} className="h-full">
              <TiltCard className="rounded-lens">
                <SavedCard item={item} onRemove={() => removeItem.mutate(item.item_id)} />
              </TiltCard>
            </m.div>
          ))}
        </m.div>
      )}
    </section>
  );
}

function SavedCard({ item, onRemove }: { item: SavedItem; onRemove: () => void }) {
  return (
    <div className="glass relative flex h-full items-center gap-3 rounded-lens p-3">
      <button
        type="button"
        onClick={onRemove}
        aria-label={`Remove ${item.title}`}
        className="absolute right-2 top-2 flex size-6 items-center justify-center rounded-full
          bg-night/60 text-[0.8rem] text-faint transition-colors hover:text-red-300"
      >
        ✕
      </button>
      {item.image_url ? (
        <img
          src={item.image_url}
          alt=""
          loading="lazy"
          className="h-[64px] w-[46px] shrink-0 rounded-md border border-glass-line object-cover"
        />
      ) : (
        <div className="shrink-0">
          <PosterPlaceholder posterSize="h-[64px] w-[46px]" icon="🎞" />
        </div>
      )}
      <div className="min-w-0 pr-4">
        <div className="truncate text-[0.95rem] font-semibold tracking-[-0.01em]">{item.title}</div>
        <div className="mt-0.5 font-mono text-[0.72rem] text-faint">{item.category}</div>
      </div>
    </div>
  );
}
