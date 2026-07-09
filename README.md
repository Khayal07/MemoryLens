# MemoryLens

Find things you only partially remember. Describe a fragment — *"twelve people voting in one room"* — and MemoryLens returns the most likely real titles, grounded in a real catalog, with confidence scores and explanations.

> AI course final project, built as a production-grade SaaS.

## Categories

🎬 Movies · 📺 TV Series · 🎵 Songs · 📚 Books · 🎮 Games · 👤 Actors

You pick a category first; it becomes a hard retrieval filter. The AI ranks and explains real candidates — it never invents titles. When a query clearly belongs to another category, the UI offers a soft "switch?" suggestion. When no catalog item is a confident match, the AI names the real title from world knowledge instead (marked "AI knowledge").

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI (Python 3.12) |
| Frontend | React + Vite + TypeScript + Tailwind v4 + framer-motion |
| Store + Vectors | Postgres 16 + pgvector |
| Cache / rate-limit | Redis |
| Embeddings / rerank | sentence-transformers (local, bge + cross-encoder) |
| LLM reasoning | OpenAI `gpt-4.1-nano` (primary) → OpenRouter (fallback) |
| Infra | Docker Compose |

## Architecture

```
React SPA → FastAPI (routers → services → AI pipeline)
                       ├─ Postgres + pgvector  (catalog, vectors, keyword)
                       ├─ Redis                (cache, rate limit)
                       └─ OpenAI / OpenRouter   (LLM reasoning only)
   local models: embeddings + cross-encoder reranking
```

Search pipeline: validate → clean → understand → hybrid retrieve (vector + keyword + weighted RRF) → rerank → LLM reasoning → confidence → free-form fallback → response.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the design, and **[docs/](docs/README.md)** for the full documentation set — [overview](docs/OVERVIEW.md), [pipeline](docs/PIPELINE.md), [API](docs/API.md), [data model](docs/DATA-MODEL.md), [features](docs/FEATURES.md), [catalog](docs/CATALOG.md), [configuration](docs/CONFIGURATION.md), [development](docs/DEVELOPMENT.md), [security](docs/SECURITY.md), and [changelog](docs/CHANGELOG.md).

---

## Run it (Docker Desktop)

**One command, everything starts.** Make sure Docker Desktop is running first.

```bash
cp .env.example .env      # then fill OPENAI_API_KEY (see below)
docker compose up --build
```

That starts all four services: `postgres`, `redis`, `api`, `frontend`. The frontend installs its own dependencies on start, so newly added packages always work — no manual `npm install` needed.

### URLs — bookmark these

| What | URL |
|---|---|
| **App (frontend)** | **http://localhost:5173** |
| API docs (Swagger) | http://localhost:8000/docs |
| API health | http://localhost:8000/api/v1/health |

> **Port note:** in Docker the app is **always** on **5173** (fixed via `--strictPort`). If you ever ran the frontend *natively* with `npm run dev` while 5173 was already busy, Vite silently jumped to **5174** — that was the source of the 5173/5174 confusion. Inside Docker it never drifts.

### Configure the API key

`.env` needs an OpenAI key for LLM reasoning:

```
OPENAI_API_KEY=sk-...
```

Cost is tiny (`gpt-4.1-nano` ≈ $0.0003/search). OpenAI is prepaid — set a low hard limit in your OpenAI billing dashboard. If OpenAI fails, it falls back to the free OpenRouter model (`OPENROUTER_API_KEY`, optional but slower).

### Seed the catalog

First run only — load the real catalog data:

```bash
docker compose exec api python -m scripts.ingest --all --source fixture
```

Then search at http://localhost:5173.

---

## Everyday commands

```bash
docker compose up -d            # start in background
docker compose down             # stop everything
docker compose logs -f frontend # watch frontend logs
docker compose logs -f api      # watch API logs
docker compose ps               # see what's running + ports
```

## Evaluation — how accurate is it, really?

We benchmark on a fixed dataset of **48 fuzzy-memory queries** (8 per category,
easy/medium/hard), each with a known correct answer that exists in the catalog
(`backend/eval/dataset.json`). Two numbers matter:

- **recall@1** — how often the correct answer is the #1 result.
- **MRR** — on average, how close to the top the correct answer lands (1.0 = always first).

| Configuration | recall@1 | recall@5 | MRR |
|---|---|---|---|
| Keyword search only | 54% | 71% | 0.625 |
| Vector search only | 54% | 77% | 0.644 |
| Hybrid (vector + keyword, no rerank) | 58% | 77% | 0.653 |
| Hybrid + cross-encoder rerank | 54% | 79% | 0.648 |
| Hybrid + rerank + HyDE | 56% | 79% | 0.662 |
| **Full pipeline (+ LLM reasoning + free-form fallback)** | **92%** | **96%** | **0.938** |

What the table says, in plain words:

- Retrieval alone finds the right item in its top-5 about 8 times out of 10; hybrid
  fusion and reranking mostly improve *depth* (recall@5), not the #1 spot.
- The big jump comes from the LLM layer: reasoning re-orders the shortlist and the
  free-form fallback rescues queries the small catalog simply can't answer
  (e.g. weak actor bios) — top-1 accuracy goes **54% → 92%**.
- Hard queries (no title words at all) score 82% top-1 on the full pipeline vs 35%
  on retrieval alone.

Reproduce it yourself (results are saved to `backend/eval/results/`):

```bash
docker compose exec api python -m scripts.run_eval                  # retrieval baseline, free, ~40s
docker compose exec api python -m scripts.run_eval --no-rerank --label no-rerank
docker compose exec api python -m scripts.run_eval --leg vector --label vector-only
docker compose exec api python -m scripts.run_eval --full --label full  # whole pipeline, uses the LLM (~$0.03)
```

Full run details and per-category breakdowns: [backend/eval/RESULTS.md](backend/eval/RESULTS.md).

## Troubleshooting

**The site won't open at http://localhost:5173**

1. Check the frontend container is actually up:
   ```bash
   docker compose ps
   ```
   You should see `memorylens-frontend-1` with `Up` status. If it's missing or `Exited`, it crashed on start.
2. Read why:
   ```bash
   docker compose logs frontend --tail 30
   ```
3. `Cannot find package '@tailwindcss/vite'` (or any missing package): the container's `node_modules` volume is stale after a dependency was added. Rebuild and renew the volume:
   ```bash
   docker compose up -d --build --force-recreate --renew-anon-volumes frontend
   ```
   (The `command:` in `docker-compose.yml` now runs `npm install` on every start, so this should be self-healing going forward.)

**API returns 404 on /health** — the health endpoint is `/api/v1/health`, not `/health`. Swagger is at `/docs`.

**Nothing responds** — confirm Docker Desktop itself is running, then `docker compose up -d`.

---

## Deploying to production

`docker-compose.yml` is the **development** stack (Vite dev server, `--reload`,
Postgres/Redis published to the host). For a public deployment use
`docker-compose.prod.yml`, which serves a built static frontend via nginx, runs the
API without reload, and keeps the database and cache on the internal network only.

1. **Create `.env.prod`** from `.env.example` and set **strong** secrets:
   ```bash
   JWT_SECRET=$(openssl rand -hex 32)      # required — the API won't start otherwise
   POSTGRES_USER=memorylens_prod
   POSTGRES_PASSWORD=$(openssl rand -base64 32)
   REDIS_PASSWORD=$(openssl rand -base64 32)
   REDIS_URL=redis://:<that-redis-password>@redis:6379/0
   METRICS_TOKEN=$(openssl rand -hex 16)   # required to scrape /metrics in prod
   ENV=production
   CORS_ORIGINS=https://your-domain
   ```
   Also set the real `OPENAI_API_KEY` and ingestion keys. **Rotate any key that has
   ever sat in a shared `.env`.**

2. **Launch:**
   ```bash
   docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
   ```

3. **Front it with TLS.** Put nginx/Caddy/Traefik in front of the `frontend` service
   (port 8080) to terminate HTTPS; the app emits HSTS when `ENV=production`. The
   proxy must set `X-Forwarded-For` to the real client IP — the per-user/per-IP rate
   limiter reads it (the bundled nginx already does this).

**What `ENV=production` changes:** requires a real `JWT_SECRET` (fail-fast on
startup), hides `/docs` `/redoc` `/openapi.json`, gates `/metrics` behind
`X-Metrics-Token`, and emits HSTS.

**Cost / abuse controls:** search requires login and is capped per user by
`SEARCH_RATE_PER_MIN` (burst) and `SEARCH_DAILY_QUOTA` (hard daily ceiling), so one
account can't drain the LLM budget. Security headers (`X-Content-Type-Options`,
`X-Frame-Options`, CSP, `Referrer-Policy`) are set on every response.

---

## Status

✅ Backend (grounded RAG pipeline, hybrid retrieval, auth, history), frontend SPA
(Aurora + glass UI, Tailwind v4, framer-motion), 6 live categories with real
catalog data, observability, Docker, CI. Verified end-to-end.

**Repo:** https://github.com/Khayal07/MemoryLens
