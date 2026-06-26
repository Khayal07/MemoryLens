import type { ResultItem } from "../lib/types";
import ConfidenceMeter from "./ConfidenceMeter";

interface Props {
  result: ResultItem;
  best?: boolean;
  index: number;
  icon?: string | null;
}

export default function ResultCard({ result, best, index, icon }: Props) {
  const tags = Object.entries(result.metadata)
    .filter(([, v]) => v !== null && v !== undefined && v !== "")
    .slice(0, 4);

  return (
    <article
      className={`card${best ? " best" : ""}`}
      style={{ animationDelay: `${Math.min(index * 80, 400)}ms` }}
    >
      {result.image_url ? (
        <img className="poster" src={result.image_url} alt="" loading="lazy" />
      ) : (
        <div className="poster placeholder" aria-hidden="true">
          {icon ?? "🎞"}
        </div>
      )}
      <div>
        <ConfidenceMeter value={result.confidence} />
        <h3 className="card-title">{result.title}</h3>
        {result.reason ? (
          <p className="reason">{result.reason}”</p>
        ) : (
          <p className="desc">{result.description}</p>
        )}
        {result.reason && <p className="desc">{result.description}</p>}
        {tags.length > 0 && (
          <div className="meta">
            {tags.map(([k, v]) => (
              <span className="tag" key={k}>
                {k}: {String(Array.isArray(v) ? v.join(", ") : v)}
              </span>
            ))}
          </div>
        )}
        {result.source_url && (
          <a className="source" href={result.source_url} target="_blank" rel="noreferrer">
            View source ↗
          </a>
        )}
      </div>
    </article>
  );
}
