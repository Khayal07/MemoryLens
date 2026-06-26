import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
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
      <section className="hero">
        <span className="eyebrow">Half-remembered? Start here</span>
        <h1>
          You almost have it.
          <br />
          <em>Bring it into focus.</em>
        </h1>
        <p>
          Describe the fragment you remember — we search a real catalog and surface the
          most likely match, with how sure we are and why.
        </p>
      </section>

      {isLoading && <p className="loading">Opening the lens…</p>}
      {isError && <p className="empty">Couldn't load categories. Is the API running?</p>}

      <div className="grid">
        {data?.map((c) => (
          <button
            key={c.key}
            className="cat"
            onClick={() => navigate(`/search/${c.key}`)}
          >
            <span className="cat-icon" aria-hidden="true">
              {c.icon}
            </span>
            <div className="cat-name">{c.display_name}</div>
            <div className="cat-desc">{DESC[c.key] ?? "Search this category"}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
