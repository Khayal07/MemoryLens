# MemoryLens — Architecture

MemoryLens turns a fuzzy memory ("twelve people voting in one room") into real,
grounded matches with a confidence score and an explanation. It never invents
titles: the LLM only ranks and explains candidates retrieved from a real catalog.

## System

```
┌────────────┐   /api/v1    ┌──────────────────────────────────────────┐
│  React SPA │ ───────────▶ │              FastAPI (api)               │
│ Vite + TS  │ ◀─────────── │  routers → services → AI pipeline        │
└────────────┘              │                                          │
                            │   ┌─ Postgres + pgvector (catalog,       │
                            │   │   vectors, tsvector keyword)         │
                            │   ├─ Redis (rate limit + search cache)   │
                            │   └─ OpenRouter (LLM reasoning only)      │
                            └───────────────┬──────────────────────────┘
                              local models: bge embeddings + cross-encoder rerank
```

Layered (Clean Architecture), dependencies point inward:
`api` → `services` → `ai` / `domain` ← `infra`. The pipeline depends on **ports**
(`app/ai/ports.py`) so each stage is swappable.

## Search pipeline (`app/ai/pipeline.py`)

```
validate → clean (+injection scrub) → hybrid retrieve → rerank → LLM reason →
confidence → alternatives → mismatch suggestion → response
```

| Stage | Where | Notes |
|---|---|---|
| Validate / clean | `ai/cleaning.py` | length, whitespace, prompt-injection scrub |
| Hybrid retrieve | `ai/retriever.py` | pgvector cosine kNN + tsvector keyword, **category-filtered**, fused by RRF (`ai/fusion.py`) |
| Rerank | `ai/reranker.py` | local cross-encoder over the fused top-N |
| Reason | `ai/llm.py` + `ai/prompts/` | OpenRouter; selects/explains candidates only; strict JSON (`ai/reasoning.py`) with repair retry |
| Confidence | `ai/confidence.py` | blended: LLM rating + sigmoid(rerank) + retrieval — *computed, not claimed* |
| Mismatch | pipeline | soft "switch category?" suggestion; never auto-switches |

Steps before the LLM are deterministic and free (local models). Only reasoning
hits the network. On any LLM/parse failure the pipeline falls back to rerank order.

## Data model (`app/infra/models.py`)

`users · categories · items · item_embeddings(vector384, tsvector) · searches · search_results`

Per-category fields live in `items.metadata (jsonb)`, so a new category needs **no
schema change** — only a new ingestion adapter (`app/ingest/`) and a `categories`
row. HNSW index on the vector, GIN on the tsvector.

## Cross-cutting

- **Auth**: Argon2 hashing, JWT access/refresh (`core/security.py`).
- **Errors**: typed `AppError` → `{error:{code,message}}` envelope.
- **Rate limiting**: Redis fixed-window, tighter on `/search` (`core/rate_limit.py`).
- **Caching**: identical fragments skip the pipeline within TTL (`infra/cache.py`).
- **Observability**: structured JSON logs + request id (`core/logging.py`,
  `core/middleware.py`), Prometheus `/metrics`, `/health` + `/readyz` (db + redis).

## Extending

Add a category: append to `app/domain/categories.py`, add an ingestion adapter in
`app/ingest/`, run `python -m scripts.ingest --category <key>`. Nothing in the
pipeline or API changes.
