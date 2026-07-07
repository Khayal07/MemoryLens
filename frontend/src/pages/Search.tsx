import { useMutation, useQuery } from "@tanstack/react-query";
import { m } from "framer-motion";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import MismatchBanner from "../components/MismatchBanner";
import ResultCard from "../components/ResultCard";
import SimilarItems from "../components/SimilarItems";
import ShareButton from "../components/ShareButton";
import VoiceInput from "../components/VoiceInput";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import Eyebrow from "../components/ui/Eyebrow";
import Skeleton from "../components/ui/Skeleton";
import Alert from "../components/ui/Alert";
import { fadeUp, stagger } from "../components/motion/variants";
import { api, ApiError } from "../lib/api";

const EXAMPLES: Record<string, string[]> = {
  movies: ["Twelve people arguing in one room over a verdict", "A man plants an idea inside a dream"],
  tv: ["A chemistry teacher starts cooking drugs", "Kids and a monster from another dimension"],
  songs: ["A man singing about walking in the rain", "An operatic rock song about killing a man"],
  books: ["A hobbit, a dragon, and a stolen treasure", "A boy finds a dragon egg and learns magic"],
  games: ["A blue hedgehog collecting rings at high speed", "A hero with a sword saving a princess in an open world"],
  actors: ["He always plays mafia and crime bosses", "The actor from Titanic and Inception"],
};

export default function Search() {
  const { category = "" } = useParams();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const { data: categories } = useQuery({ queryKey: ["categories"], queryFn: api.categories });
  const current = categories?.find((c) => c.key === category);

  const mutation = useMutation({ mutationFn: (q: string) => api.search(category, q) });

  function submit(text: string) {
    const q = text.trim();
    if (q.length < 3) return;
    mutation.mutate(q);
  }

  const response = mutation.data;
  const error = mutation.error as ApiError | null;
  // Similar items hang off the best *grounded* match; a free-form hero (item_id 0)
  // has no catalog neighbours, so fall through to the first real catalog result.
  const bestGrounded = response?.results.find((r) => r.item_id > 0);

  return (
    <div>
      <div className="mb-[22px] flex items-center justify-between gap-3">
        <span className="glass inline-flex items-center gap-2 rounded-full px-3.5 py-[7px] text-[0.9rem] font-semibold">
          <span aria-hidden="true">{current?.icon ?? "🔎"}</span>
          {current?.display_name ?? category}
        </span>
        <Link
          to="/"
          className="rounded-[10px] px-3 py-2 text-[0.92rem] font-medium text-muted transition-colors hover:bg-raised hover:text-ink"
        >
          ← All categories
        </Link>
      </div>

      <form
        className="glass-strong flex gap-2.5 rounded-2xl p-2.5
          transition-shadow focus-within:shadow-glow focus-within:ring-2 focus-within:ring-violet/50"
        onSubmit={(e) => {
          e.preventDefault();
          submit(query);
        }}
      >
        <textarea
          autoFocus
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit(query);
            }
          }}
          placeholder={`Describe the ${current?.display_name?.toLowerCase() ?? ""} you half-remember…`}
          aria-label="Describe what you remember"
          className="max-h-40 min-h-7 flex-1 resize-none bg-transparent px-3 py-3 text-[1.05rem] leading-[1.45] text-ink outline-none placeholder:text-faint"
        />
        <VoiceInput value={query} onChange={setQuery} />
        <Button type="submit" disabled={mutation.isPending} className="self-stretch">
          {mutation.isPending ? "Focusing…" : "Recall"}
        </Button>
      </form>

      {!response && !mutation.isPending && (
        <>
          <p className="mt-3 text-[0.85rem] text-faint">
            Press Enter to search · Shift+Enter for a new line
          </p>
          <m.div
            className="mt-3.5 flex flex-wrap gap-2"
            variants={stagger(0.06)}
            initial="hidden"
            animate="show"
          >
            {(EXAMPLES[category] ?? []).map((ex) => (
              <m.button
                key={ex}
                variants={fadeUp}
                onClick={() => {
                  setQuery(ex);
                  submit(ex);
                }}
                className="glass rounded-full px-3 py-1.5 text-[0.82rem] text-muted transition-colors hover:border-violet/60 hover:text-ink"
              >
                {ex}
              </m.button>
            ))}
          </m.div>
        </>
      )}

      {error && <div className="mt-4"><Alert>{error.message}</Alert></div>}

      {mutation.isPending && (
        <div className="mt-7 space-y-3.5">
          <Skeleton className="h-[214px]" />
          <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2">
            <Skeleton className="h-[152px] opacity-70" />
            <Skeleton className="h-[152px] opacity-50" />
          </div>
        </div>
      )}

      {response?.suggestion && (
        <MismatchBanner
          suggestion={response.suggestion}
          onSwitch={(cat) => {
            mutation.reset();
            navigate(`/search/${cat}`);
          }}
        />
      )}

      {response && response.results.length === 0 && (
        <EmptyState
          title={`Nothing matched in ${current?.display_name ?? category}.`}
          hint="Try more details — a scene, a character, a feeling."
        />
      )}

      {response && response.results.length > 0 && (
        <div key={response.query}>
          <div className="mb-4 mt-8 flex items-center justify-between gap-3">
            <Eyebrow>Best match</Eyebrow>
            <ShareButton searchId={response.search_id} />
          </div>
          <m.div variants={stagger()} initial="hidden" animate="show">
            <ResultCard
              result={response.results[0]}
              best
              icon={current?.icon}
              searchId={response.search_id}
            />
          </m.div>

          {response.results.length > 1 && (
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
                {response.results.slice(1).map((r, i) => (
                  <ResultCard
                    key={`${r.item_id}-${i}`}
                    result={r}
                    icon={current?.icon}
                    searchId={response.search_id}
                  />
                ))}
              </m.div>
            </>
          )}

          {bestGrounded && <SimilarItems itemId={bestGrounded.item_id} icon={current?.icon} />}
        </div>
      )}
    </div>
  );
}
