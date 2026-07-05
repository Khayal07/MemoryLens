import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, m } from "framer-motion";
import { useState } from "react";
import { useAuth } from "../features/auth/AuthContext";
import { api } from "../lib/api";
import type { Collection } from "../lib/types";
import { cn } from "../lib/cn";

interface Props {
  itemId: number;
}

/** Bookmark control: saves a grounded catalog item into one of the user's named
 *  collections. Hidden for anonymous users and for free-form answers (item_id 0),
 *  which have no catalog row to reference. */
export default function SaveButton({ itemId }: Props) {
  const { isAuthenticated } = useAuth();
  const [open, setOpen] = useState(false);

  if (!isAuthenticated || itemId <= 0) return null;

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label="Save to a collection"
        aria-expanded={open}
        className="glass flex size-9 items-center justify-center rounded-full text-[1rem]
          text-muted transition-colors hover:border-violet/50 hover:text-ink
          focus-visible:outline-2 focus-visible:outline-violet-soft"
      >
        ✦
      </button>

      <AnimatePresence>
        {open && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} aria-hidden="true" />
            <Picker itemId={itemId} onClose={() => setOpen(false)} />
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

function Picker({ itemId, onClose }: { itemId: number; onClose: () => void }) {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const { data: collections, isLoading } = useQuery({
    queryKey: ["collections"],
    queryFn: api.collections,
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ["collections"] });

  const toggle = useMutation({
    mutationFn: ({ col, saved }: { col: Collection; saved: boolean }) =>
      saved ? api.removeFromCollection(col.id, itemId) : api.addToCollection(col.id, itemId),
    onSuccess: invalidate,
  });

  const create = useMutation({
    mutationFn: async (n: string) => {
      const col = await api.createCollection(n);
      await api.addToCollection(col.id, itemId);
    },
    onSuccess: () => {
      setName("");
      invalidate();
    },
  });

  return (
    <m.div
      initial={{ opacity: 0, y: -6, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -6, scale: 0.97 }}
      transition={{ duration: 0.16 }}
      className="glass-strong absolute right-0 z-50 mt-2 w-64 rounded-xl p-2.5 shadow-glass"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="px-1 pb-1.5 text-[0.72rem] font-semibold uppercase tracking-wide text-faint">
        Save to
      </div>

      {isLoading ? (
        <div className="px-1 py-2 text-[0.85rem] text-muted">Loading…</div>
      ) : (
        <div className="max-h-52 space-y-1 overflow-y-auto">
          {(collections ?? []).map((col) => {
            const saved = col.items.some((i) => i.item_id === itemId);
            return (
              <button
                key={col.id}
                type="button"
                onClick={() => toggle.mutate({ col, saved })}
                className={cn(
                  "flex w-full items-center justify-between gap-2 rounded-lg px-2.5 py-2 text-left text-[0.9rem]",
                  "transition-colors hover:bg-white/[0.05]",
                  saved ? "text-ink" : "text-muted",
                )}
              >
                <span className="truncate">{col.name}</span>
                <span className={cn("text-[0.9rem]", saved ? "text-violet-soft" : "text-faint")}>
                  {saved ? "✓" : "+"}
                </span>
              </button>
            );
          })}
          {collections?.length === 0 && (
            <div className="px-2.5 py-1.5 text-[0.82rem] text-faint">No collections yet.</div>
          )}
        </div>
      )}

      <form
        className="mt-2 flex gap-1.5 border-t border-glass-line pt-2.5"
        onSubmit={(e) => {
          e.preventDefault();
          const n = name.trim();
          if (n) create.mutate(n);
        }}
      >
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="New collection…"
          maxLength={80}
          className="min-w-0 flex-1 rounded-lg border border-glass-line bg-night/50 px-2.5 py-1.5
            text-[0.85rem] text-ink placeholder:text-faint focus:border-violet focus:outline-none"
        />
        <button
          type="submit"
          disabled={!name.trim() || create.isPending}
          className="rounded-lg bg-gradient-to-r from-violet-soft to-amber px-3 py-1.5 text-[0.85rem]
            font-semibold text-[#14122b] disabled:opacity-50"
        >
          Add
        </button>
      </form>

      <button
        type="button"
        onClick={onClose}
        className="mt-2 w-full rounded-lg px-2.5 py-1.5 text-[0.78rem] text-faint hover:text-muted"
      >
        Done
      </button>
    </m.div>
  );
}
