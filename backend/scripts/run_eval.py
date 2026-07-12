"""Retrieval benchmark: recall@k + MRR over eval/dataset.json.

    docker compose exec api python -m scripts.run_eval                    # baseline (hybrid + rerank)
    docker compose exec api python -m scripts.run_eval --no-rerank --label no-rerank
    docker compose exec api python -m scripts.run_eval --leg vector --label vector-only
    docker compose exec api python -m scripts.run_eval --leg keyword --label keyword-only
    docker compose exec api python -m scripts.run_eval --hyde --label hyde   # +1 LLM call/query
    docker compose exec api python -m scripts.run_eval --full --label full   # full pipeline incl. LLM

The default mode exercises only the local retrieval stack (embeddings + pgvector +
tsvector + cross-encoder) — no LLM, no network, free, deterministic. `--hyde` adds the
HyDE query-expansion LLM call; `--full` runs the whole SearchPipeline (reasoning +
free-form fallback) and scores the FINAL top-k the user would see.

Each run prints a metrics table and writes a timestamped JSON (config echo + per-case
ranks) to eval/results/ so ablations can be compared side by side in the report.
Expected titles are matched loosely via app.ai.matching.same_title, so franchise
variants ("The Last Of Us Remastered") count as hits.
"""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from app.ai.types import Candidate

EVAL_DIR = Path(__file__).resolve().parent.parent / "eval"
DATASET = EVAL_DIR / "dataset.json"
RESULTS_DIR = EVAL_DIR / "results"


# --- metrics (pure, unit-tested in tests/test_eval_metrics.py) ---------------------


def find_rank(expected: list[str], titles: list[str]) -> int | None:
    """1-based rank of the first result matching ANY expected title, else None."""
    from app.ai.matching import same_title

    for pos, title in enumerate(titles, start=1):
        if any(same_title(exp, title) for exp in expected):
            return pos
    return None


def recall_at_k(ranks: list[int | None], k: int) -> float:
    """Fraction of cases whose correct answer appeared within the top k."""
    if not ranks:
        return 0.0
    return sum(1 for r in ranks if r is not None and r <= k) / len(ranks)


def mean_reciprocal_rank(ranks: list[int | None]) -> float:
    """Average of 1/rank (a miss contributes 0)."""
    if not ranks:
        return 0.0
    return sum(1.0 / r for r in ranks if r is not None) / len(ranks)


# --- retrieval variants -------------------------------------------------------------


def _to_candidates(rows) -> list[Candidate]:
    """(Item, score) rows from a single retriever leg → scored Candidates."""
    return [
        Candidate(
            item_id=item.id,
            title=item.title,
            description=item.description or "",
            retrieval_score=score,
        )
        for item, score in rows
    ]


def _retrieve(db, retriever, category_id: int, query: str, leg: str, embed_text: str):
    """Candidates in ranked order for the chosen leg (hybrid = fused, RRF order)."""
    if leg == "hybrid":
        return retriever.search(db, category_id, query, k=30, embed_text=embed_text)
    if leg == "vector":
        vec = retriever.embedder.embed_query(embed_text)
        rows = retriever._vector_search(db, category_id, vec)
        return _to_candidates(sorted(rows, key=lambda r: r[1], reverse=True))
    if leg == "keyword":
        rows = retriever._keyword_search(db, category_id, query)
        return _to_candidates(sorted(rows, key=lambda r: r[1], reverse=True))
    raise ValueError(f"unknown leg '{leg}'")


def _hyde_expand(llm, category_name: str, query: str) -> str:
    """Best-effort HyDE expansion, mirroring pipeline._expand_query."""
    from app.ai.llm import LLMError
    from app.ai.prompts import hyde

    try:
        system = hyde.SYSTEM_PROMPT.format(category=category_name)
        hypothesis = llm.complete_text(
            system, hyde.build_user_prompt(category_name, query)
        ).strip()
    except LLMError as exc:
        print(f"    hyde failed ({exc}); using raw query")
        return query
    return f"{query}\n{hypothesis}" if hypothesis else query


def _song_guess_expand(llm, query: str) -> tuple[str, str] | None:
    """Songs-only guess expansion, mirroring pipeline._expand_song. Returns
    (keyword_query, embed_text) or None to fall back to the raw query."""
    from app.ai.llm import LLMError
    from app.ai.prompts import song_guess
    from app.ai.song_guess import SongGuessParseError, parse_song_guess

    try:
        raw = llm.complete_json(song_guess.SYSTEM_PROMPT, song_guess.build_user_prompt(query))
        guess = parse_song_guess(raw)
    except (SongGuessParseError, LLMError) as exc:
        print(f"    song-guess failed ({exc}); using raw query")
        return None
    if not guess.title.strip():
        return None
    who = f" {guess.artist}".rstrip()
    keyword_query = f"{query} {guess.title}{who}".strip()
    embed_text = f"{query}\n{guess.title} by {guess.artist}. {guess.description}".strip()
    return keyword_query, embed_text


# --- run ---------------------------------------------------------------------------


def run(args) -> dict:
    from sqlalchemy import select

    from app.ai.reranker import get_reranker
    from app.ai.retriever import HybridRetriever
    from app.core.config import get_settings
    from app.infra.db import SessionLocal
    from app.infra.models import Category

    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    cases = dataset["cases"]
    if args.category:
        cases = [c for c in cases if c["category"] == args.category]

    retriever = HybridRetriever()
    reranker = get_reranker() if args.rerank else None
    settings = get_settings()
    top_n = max(args.k, settings.rerank_top_n)

    llm = None
    if args.hyde or args.full or args.song_guess:
        from app.ai.llm import LLMClient

        llm = LLMClient()
    pipeline = None
    if args.full:
        from app.ai.pipeline import get_pipeline

        pipeline = get_pipeline()

    per_case: list[dict] = []
    started = time.time()
    with SessionLocal() as db:
        cat_ids = {
            key: id_
            for key, id_ in db.execute(select(Category.key, Category.id)).all()
        }
        for case in cases:
            query, expected = case["query"], case["expected"]
            if pipeline is not None:
                # Full pipeline: score what the user actually sees (LLM order,
                # free-form hero included). Materialized gpt rows are rolled back below.
                response = pipeline.run(db, case["category"], query, max_results=args.k)
                titles = [r.title for r in response.results]
            else:
                embed_text = query
                keyword_query = query
                if args.song_guess and case["category"] == "songs":
                    expansion = _song_guess_expand(llm, query)
                    if expansion is not None:
                        keyword_query, embed_text = expansion
                elif args.hyde:
                    cat_name = case["category"].capitalize()
                    embed_text = _hyde_expand(llm, cat_name, query)
                candidates = _retrieve(
                    db, retriever, cat_ids[case["category"]], keyword_query, args.leg, embed_text
                )
                if reranker is not None:
                    candidates = reranker.rerank(query, candidates, top_n=top_n)
                titles = [c.title for c in candidates[: args.k]]

            rank = find_rank(expected, titles)
            per_case.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "difficulty": case["difficulty"],
                    "expected": expected[0],
                    "rank": rank,
                    "top": titles[:3],
                }
            )
            mark = "MISS" if rank is None else f"#{rank}"
            print(f"  [{case['id']}] {mark:>4}  {expected[0]}")
        db.rollback()  # never persist eval side effects (e.g. --full gpt rows)

    ranks = [c["rank"] for c in per_case]
    summary = {
        "label": args.label,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config": {
            "mode": "full-pipeline" if args.full else "retrieval",
            "leg": args.leg,
            "rerank": args.rerank,
            "hyde": args.hyde,
            "song_guess": args.song_guess,
            "k": args.k,
            "cases": len(per_case),
        },
        "metrics": {
            "recall@1": round(recall_at_k(ranks, 1), 3),
            "recall@3": round(recall_at_k(ranks, 3), 3),
            f"recall@{args.k}": round(recall_at_k(ranks, args.k), 3),
            "mrr": round(mean_reciprocal_rank(ranks), 3),
        },
        "by_category": _group_metrics(per_case, "category", args.k),
        "by_difficulty": _group_metrics(per_case, "difficulty", args.k),
        "seconds": round(time.time() - started, 1),
        "cases": per_case,
    }
    return summary


def _group_metrics(per_case: list[dict], field: str, k: int) -> dict:
    groups: dict[str, list[int | None]] = {}
    for c in per_case:
        groups.setdefault(c[field], []).append(c["rank"])
    return {
        name: {
            "recall@1": round(recall_at_k(ranks, 1), 3),
            f"recall@{k}": round(recall_at_k(ranks, k), 3),
            "mrr": round(mean_reciprocal_rank(ranks), 3),
            "n": len(ranks),
        }
        for name, ranks in sorted(groups.items())
    }


def _print_summary(summary: dict) -> None:
    m = summary["metrics"]
    print(f"\n=== {summary['label']} ({summary['config']['cases']} cases, "
          f"{summary['seconds']}s) ===")
    print("  " + "  ".join(f"{k} {v:.1%}" if k != "mrr" else f"mrr {v:.3f}"
                           for k, v in m.items()))
    for section in ("by_category", "by_difficulty"):
        print(f"  -- {section[3:]}")
        for name, g in summary[section].items():
            r1, mrr, n = g["recall@1"], g["mrr"], g["n"]
            print(f"     {name:<10} recall@1 {r1:.1%}  mrr {mrr:.3f}  (n={n})")
    misses = [c for c in summary["cases"] if c["rank"] is None]
    if misses:
        print("  -- misses")
        for c in misses:
            print(f"     {c['id']}: wanted '{c['expected']}', top: {c['top']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="baseline", help="name for the results file")
    parser.add_argument("--k", type=int, default=5, help="results scored per query")
    parser.add_argument("--leg", choices=["hybrid", "vector", "keyword"], default="hybrid")
    parser.add_argument("--no-rerank", dest="rerank", action="store_false",
                        help="score raw retrieval order (skip the cross-encoder)")
    parser.add_argument("--hyde", action="store_true",
                        help="expand queries with HyDE (adds 1 LLM call per query)")
    parser.add_argument("--song-guess", dest="song_guess", action="store_true",
                        help="songs-only lyric-aware guess expansion (1 LLM call per song query)")
    parser.add_argument("--full", action="store_true",
                        help="run the whole SearchPipeline (LLM reasoning + free-form)")
    parser.add_argument("--category", help="only run one category's cases")
    args = parser.parse_args()

    summary = run(args)
    _print_summary(summary)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = RESULTS_DIR / f"{stamp}_{args.label}.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {out.relative_to(EVAL_DIR.parent)}")


if __name__ == "__main__":
    main()
