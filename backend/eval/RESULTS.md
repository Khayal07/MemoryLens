# Evaluation results — 2026-07-09

Dataset: `eval/dataset.json` — 48 fuzzy-memory queries, 6 categories × 8, tagged
easy (13) / medium (18) / hard (17). Every expected title exists in the catalog with
an embedding, so retrieval can always find it in principle. Matching is loose
(`app.ai.matching.same_title`), so franchise variants count as hits.

Runner: `python -m scripts.run_eval` (inside the api container). Raw per-case JSON
for every run below is in `eval/results/`.

## Headline table

| Run | Mode | recall@1 | recall@3 | recall@5 | MRR | Time |
|---|---|---|---|---|---|---|
| keyword-only | tsvector + rerank | 54.2% | 70.8% | 70.8% | 0.625 | 49s |
| vector-only | pgvector + rerank | 54.2% | 72.9% | 77.1% | 0.644 | 56s |
| no-rerank | hybrid RRF, raw order | 58.3% | 72.9% | 77.1% | 0.653 | 5s |
| baseline | hybrid RRF + cross-encoder | 54.2% | 72.9% | 79.2% | 0.648 | 42s |
| hyde | baseline + HyDE expansion (1 LLM call/query) | 56.2% | 75.0% | 79.2% | 0.662 | 139s |
| **full-pipeline** | + LLM reasoning + free-form fallback | **91.7%** | **95.8%** | **95.8%** | **0.938** | 337s |

## Per-category recall@1

| Category | baseline (retrieval) | full pipeline |
|---|---|---|
| movies | 75.0% | 100% |
| tv | 87.5% | 100% |
| songs | 50.0% | 87.5% |
| books | 37.5% | 100% |
| games | 50.0% | 75.0% |
| actors | 25.0% | 87.5% |

## Per-difficulty recall@1

| Difficulty | baseline (retrieval) | full pipeline |
|---|---|---|
| easy | 76.9% | 100% |
| medium | 55.6% | 94.4% |
| hard | 35.3% | 82.4% |

## Findings

1. **The LLM layer is what makes the product work.** Retrieval alone puts the right
   answer first only 54% of the time; the full pipeline reaches 92%. Two mechanisms:
   the reasoning step re-orders the reranked shortlist (the answer was usually
   *retrieved* — recall@5 79% — just not first), and the free-form fallback answers
   from world knowledge when the catalog row is unfindable.

2. **Actors is retrieval's weakest category (25%).** Catalog bios describe careers
   ("American actor born in…") while memories describe *roles* ("plays neo…"), so
   there is little lexical or semantic overlap. The free-form fallback fixes exactly
   this: 87.5% on the full pipeline.

3. **Hybrid fusion earns its keep on depth, not the top spot.** Keyword-only and
   vector-only tie at 54.2% recall@1, but hybrid+rerank lifts recall@5 from
   70.8%/77.1% to 79.2% — a deeper, better shortlist, which is what the LLM stage
   actually consumes.

4. **The cross-encoder rerank is roughly confidence-neutral on recall@1**
   (58.3% raw RRF vs 54.2% reranked) but adds recall@5 (77.1% → 79.2%) and fixes
   individual cases (Interstellar: MISS → #1). Its real value shows downstream:
   rerank scores feed the confidence blend.

5. **HyDE helps a little** (+2pp recall@1, +2.1pp recall@3, MRR 0.648 → 0.662) but
   costs one extra LLM call per query. Keeping it off by default (`hyde_enabled=false`)
   is a defensible latency/cost trade-off.

6. **Remaining full-pipeline misses (2/48)** are both free-form hallucinations by
   the small gpt-4.1-nano model on hard queries: gam-03 (Witcher 3 → "Monster
   Hunter: World") and act-07 (Anthony Hopkins → "Jodie Foster" — the model named
   the wrong Silence-of-the-Lambs lead). A larger identify model would likely fix
   both; this is the documented small-model trade-off.

## Reproduce

```bash
docker compose exec api python -m scripts.run_eval --label baseline
docker compose exec api python -m scripts.run_eval --no-rerank --label no-rerank
docker compose exec api python -m scripts.run_eval --leg vector --label vector-only
docker compose exec api python -m scripts.run_eval --leg keyword --label keyword-only
docker compose exec api python -m scripts.run_eval --hyde --label hyde
docker compose exec api python -m scripts.run_eval --full --label full-pipeline
```

Retrieval modes are LLM-free and deterministic. `--hyde` ≈ $0.01, `--full` ≈ $0.03
with gpt-4.1-nano. `--full` rolls back any materialized free-form rows, so the
database is left untouched.
