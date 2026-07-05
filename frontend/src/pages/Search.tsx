import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import MismatchBanner from "../components/MismatchBanner";
import ResultCard from "../components/ResultCard";
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

  const mutation = useMutation({
    mutationFn: (q: string) => api.search(category, q),
  });

  function submit(text: string) {
    const q = text.trim();
    if (q.length < 3) return;
    mutation.mutate(q);
  }

  const response = mutation.data;
  const error = mutation.error as ApiError | null;

  return (
    <div>
      <div className="searchhead">
        <span className="chip">
          <span aria-hidden="true">{current?.icon ?? "🔎"}</span>
          {current?.display_name ?? category}
        </span>
        <Link to="/" className="nav-link">
          ← All categories
        </Link>
      </div>

      <form
        className="recall"
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
        />
        <button className="btn btn-primary" type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Focusing…" : "Recall"}
        </button>
      </form>

      {!response && !mutation.isPending && (
        <>
          <p className="hint">Press Enter to search · Shift+Enter for a new line</p>
          <div className="examples">
            {(EXAMPLES[category] ?? []).map((ex) => (
              <button
                key={ex}
                className="example"
                onClick={() => {
                  setQuery(ex);
                  submit(ex);
                }}
              >
                {ex}
              </button>
            ))}
          </div>
        </>
      )}

      {error && <div className="alert">{error.message}</div>}

      {mutation.isPending && (
        <div style={{ marginTop: 28 }}>
          <div className="skeleton" />
          <div className="skeleton" style={{ opacity: 0.6 }} />
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
        <p className="empty">
          Nothing matched in {current?.display_name ?? category}. Try more details — a
          scene, a character, a feeling.
        </p>
      )}

      {response && response.results.length > 0 && (
        <>
          <div className="results-label">
            <span className="eyebrow">Best match</span>
          </div>
          <ResultCard result={response.results[0]} best index={0} icon={current?.icon} />

          {response.results.length > 1 && (
            <>
              <div className="results-label">
                <span className="eyebrow">Other possibilities</span>
              </div>
              <div className="results-grid">
                {response.results.slice(1).map((r, i) => (
                  <ResultCard key={`${r.item_id}-${i}`} result={r} index={i + 1} icon={current?.icon} />
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
