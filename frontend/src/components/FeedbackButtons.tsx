import { useState } from "react";
import { useAuth } from "../features/auth/AuthContext";
import { api } from "../lib/api";
import { cn } from "../lib/cn";

interface Props {
  searchId: number;
  itemId: number;
}

/** Thumbs up/down on a grounded result. Votes sharpen ranking on future searches.
 *  Hidden for anonymous users and free-form answers (no catalog item to score). */
export default function FeedbackButtons({ searchId, itemId }: Props) {
  const { isAuthenticated } = useAuth();
  const [vote, setVote] = useState<1 | -1 | null>(null);

  if (!isAuthenticated || itemId <= 0) return null;

  function cast(next: 1 | -1) {
    const value = vote === next ? null : next;
    setVote(value);
    // Re-voting the same way is a no-op server-side; only send an actual vote.
    if (value !== null) void api.feedback(searchId, itemId, value).catch(() => setVote(vote));
  }

  return (
    <div className="mt-3 flex items-center gap-2" role="group" aria-label="Rate this match">
      <span className="text-[0.75rem] text-faint">Good match?</span>
      <button
        type="button"
        onClick={() => cast(1)}
        aria-pressed={vote === 1}
        aria-label="Good match"
        className={cn(
          "flex size-8 items-center justify-center rounded-full border transition-colors",
          vote === 1
            ? "border-violet/60 bg-violet/20 text-ink"
            : "border-glass-line text-muted hover:border-violet/40 hover:text-ink",
        )}
      >
        👍
      </button>
      <button
        type="button"
        onClick={() => cast(-1)}
        aria-pressed={vote === -1}
        aria-label="Bad match"
        className={cn(
          "flex size-8 items-center justify-center rounded-full border transition-colors",
          vote === -1
            ? "border-amber/60 bg-amber/20 text-ink"
            : "border-glass-line text-muted hover:border-amber/40 hover:text-ink",
        )}
      >
        👎
      </button>
    </div>
  );
}
