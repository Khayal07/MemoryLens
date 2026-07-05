import { useState } from "react";
import type { ResultItem } from "../lib/types";
import ConfidenceMeter from "./ConfidenceMeter";
import ConfidenceDial from "./ConfidenceDial";

interface Props {
  result: ResultItem;
  best?: boolean;
  index: number;
  icon?: string | null;
}

/** Internal metadata keys that should never be shown as user-facing tags. */
const HIDDEN_META = new Set(["source", "image_url", "source_url"]);

export default function ResultCard({ result, best, index, icon }: Props) {
  const [imageFailed, setImageFailed] = useState(false);
  const byAI = result.metadata?.source === "gpt-knowledge";
  const showImage = result.image_url && !imageFailed && !byAI;

  const tags = Object.entries(result.metadata)
    .filter(
      ([k, v]) => !HIDDEN_META.has(k) && v !== null && v !== undefined && v !== "",
    )
    .slice(0, 4);

  return (
    <article
      className={`card${best ? " best" : ""}${byAI ? " ai" : ""}`}
      style={{ animationDelay: `${Math.min(index * 80, 400)}ms` }}
    >
      {showImage ? (
        <img
          className="poster"
          src={result.image_url!}
          alt=""
          loading="lazy"
          onError={() => setImageFailed(true)}
        />
      ) : byAI ? (
        <div className="poster ai-placeholder" aria-hidden="true">
          <span className="ai-lens" />
        </div>
      ) : (
        <div className="poster placeholder" aria-hidden="true">
          {icon ?? "🎞"}
        </div>
      )}

      <div className="card-body">
        {byAI && <span className="ai-badge">✦ AI knowledge</span>}

        {best ? <ConfidenceDial value={result.confidence} /> : <ConfidenceMeter value={result.confidence} />}

        <h3 className="card-title">{result.title}</h3>

        {result.reason && <p className="reason">{result.reason}</p>}
        {result.description && <p className="desc">{result.description}</p>}

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
