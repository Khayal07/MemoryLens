# Configuration

All settings load from environment / `.env` via pydantic-settings
(`backend/app/core/config.py`). Copy `.env.example` → `.env` and fill in. `.env` is
gitignored and must never be committed.

## AI provider

| Variable | Default | Effect |
|---|---|---|
| `OPENAI_API_KEY` | — | **Required** for LLM reasoning. `gpt-4.1-nano`, ≈ $0.0003/search. |
| `OPENAI_MODEL` | `gpt-4.1-nano` | Primary reasoning model. |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | |
| `OPENROUTER_API_KEY` | — | Optional fallback provider (slower, free). |
| `OPENROUTER_MODEL` | `openrouter/free` | |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | |
| `LLM_FALLBACK_ENABLED` | `true` | Try OpenRouter if OpenAI fails/runs out. |

> Cost control: OpenAI is prepaid — set a low hard limit in your OpenAI billing
> dashboard. In-app, per-user search quotas cap usage (see below).

## Ingestion sources (optional — fixtures used if blank)

| Variable | Used for |
|---|---|
| `TMDB_API_KEY` | Movies/TV/actors ingestion + free-form actor photos. |
| `RAWG_API_KEY` | Games ingestion + free-form game art. |
| `OMDB_API_KEY` | Poster fallback for movies/TV (free key at omdbapi.com). |

Songs (iTunes) and books (OpenLibrary) covers need **no key**.

## Database & cache

| Variable | Default | Notes |
|---|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `memorylens` | **Change in production.** |
| `DATABASE_URL` | `postgresql+psycopg://memorylens:memorylens@postgres:5432/memorylens` | |
| `REDIS_URL` | `redis://redis:6379/0` | In prod, add a password: `redis://:<pw>@redis:6379/0`. |

## Auth

| Variable | Default | Notes |
|---|---|---|
| `JWT_SECRET` | `change-me-in-production` | **In production (`ENV != development`) the API refuses to start unless changed.** Generate: `openssl rand -hex 32`. |
| `JWT_ACCESS_TTL_MIN` | `15` | Access-token lifetime. |
| `JWT_REFRESH_TTL_DAYS` | `7` | Refresh-token lifetime. |

## Cost / abuse controls

| Variable | Default | Effect |
|---|---|---|
| `SEARCH_RATE_PER_MIN` | `10` | Per-user burst limit on `/search`. |
| `SEARCH_DAILY_QUOTA` | `50` | Hard per-user daily cap on `/search`. |
| `METRICS_TOKEN` | — | If set, `/metrics` requires header `X-Metrics-Token`. Blank in dev = open. |

## Retrieval tuning

| Variable | Default | Effect |
|---|---|---|
| `RRF_VECTOR_WEIGHT` | `1.0` | Weight of the semantic leg in fusion. |
| `RRF_KEYWORD_WEIGHT` | `0.6` | Weight of the keyword leg. |
| `RERANK_TOP_N` | `12` | Candidates handed to the cross-encoder / LLM. |
| `HYDE_ENABLED` | `false` | HyDE query expansion (adds one LLM call/search). |
| `TRANSLATE_ENABLED` | `true` | Translate non-English memories for retrieval. |
| `FREEFORM_ENABLED` | `true` | World-knowledge fallback when catalog is weak. |
| `FREEFORM_CONFIDENCE_FLOOR` | `65` | Below this grounded confidence, ask the LLM to name the item. |
| `FREEFORM_GREY_MARGIN` | `8` | Grey zone above the floor where the free-form answer verifies the grounded pick. |
| `CLARIFY_ENABLED` | `true` | Akinator clarifying question on weak matches. |
| `CLARIFY_FLOOR` | `65` | Below this, a question may be attached. |

## Local models

| Variable | Default |
|---|---|
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` (384-dim) |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L6-v2` |

Changing `EMBEDDING_MODEL` changes the vector dimension (`EMBEDDING_DIM` in
`models.py`) and requires a re-ingest.

## App

| Variable | Default | Effect |
|---|---|---|
| `ENV` | `development` | `development` keeps friendly defaults, `/docs`, open `/metrics`. Any other value enforces a real `JWT_SECRET`, hides `/docs`, gates `/metrics`, emits HSTS. |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins. |
