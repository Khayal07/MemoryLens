import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

export default function History() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["history"],
    queryFn: api.history,
  });

  return (
    <div>
      <section className="hero" style={{ marginBottom: 28 }}>
        <span className="eyebrow">Your searches</span>
        <h1 style={{ fontSize: "2rem" }}>What you've looked for</h1>
      </section>

      {isLoading && <p className="loading">Loading…</p>}
      {isError && <p className="empty">Couldn't load your history.</p>}
      {data && data.length === 0 && (
        <p className="empty">
          No searches yet. <Link to="/" className="source">Start recalling →</Link>
        </p>
      )}

      <div className="hist">
        {data?.map((h) => (
          <div className="hist-row" key={h.id}>
            <div>
              <div className="hist-q">{h.query}</div>
              <div className="hist-meta">
                {h.category} · {new Date(h.created_at).toLocaleDateString()}
              </div>
            </div>
            <span className="hist-meta">{h.result_count} results</span>
          </div>
        ))}
      </div>
    </div>
  );
}
