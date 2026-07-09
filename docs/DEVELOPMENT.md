# Development

## Prerequisites

- Docker Desktop (the whole stack runs in containers).
- Optionally a local Python 3.12 venv at `backend/.venv` for running tests fast
  (the api container image does **not** include pytest).

## Run the stack

```bash
cp .env.example .env      # fill OPENAI_API_KEY
docker compose up --build
# first run only — seed the catalog:
docker compose exec api python -m scripts.ingest --all --source fixture
```

| Service | URL |
|---|---|
| Frontend (app) | http://localhost:5173 |
| API docs (dev) | http://localhost:8000/docs |
| Health | http://localhost:8000/api/v1/health |

The frontend runs `npm install` on every start, so new deps self-heal. Ports are fixed
(`--strictPort`), so the app is always on 5173 in Docker.

## Project layout

```
backend/
  app/
    ai/            search pipeline: retriever, reranker, llm, confidence, prompts…
    api/v1/        FastAPI routers (thin — validation + delegation)
    services/      use-cases: search, auth, collections, feedback, share, analytics…
    infra/         db, redis, cache, external clients (tmdb/omdb/itunes/…), models
    ingest/        catalog adapters + runner
    domain/        canonical categories
    core/          config, security, rate_limit, errors, middleware, logging, metrics
    schemas/       Pydantic request/response DTOs
  migrations/      Alembic versions (run on startup)
  scripts/         ingest, backfills, run_eval
  tests/           188 tests
  eval/            benchmark dataset + results (RESULTS.md)
frontend/
  src/
    pages/         route components (Search, History, Collections, Landing, …)
    components/    UI + feature components (ResultCard, ConfidenceDial, VoiceInput, …)
    features/auth/ AuthContext + AuthForm
    lib/           api client, helpers
docs/              this documentation set
```

Layering (Clean Architecture, dependencies point inward):
`api → services → ai/domain ← infra`. The pipeline depends on ports
(`app/ai/ports.py`) so each stage is swappable.

## Testing

```bash
# Fast, in the local venv (container has no pytest):
backend/.venv/Scripts/python -m pytest -q            # Windows
backend/.venv/bin/python -m pytest -q                # macOS/Linux
```

Tests are unit-style — no live DB or network. External clients and Redis are faked;
there is no DB fixture, so DB-touching logic is tested via lightweight fake sessions
(see `tests/test_feedback_service.py`). Current count: **188**.

## Accuracy benchmark

```bash
docker compose exec api python -m scripts.run_eval            # retrieval baseline (free)
docker compose exec api python -m scripts.run_eval --full     # whole pipeline (uses the LLM)
```

Results save to `backend/eval/results/`; findings in
[../backend/eval/RESULTS.md](../backend/eval/RESULTS.md).

## Gotchas (hard-won)

- **Vite HMR under Docker on Windows** needs `server.watch.usePolling` (already set in
  `frontend/vite.config.ts`) — otherwise host→container file events don't fire and the
  browser serves stale transforms. If a frontend edit "isn't showing", recreate the
  frontend container.
- **api hot-reload**: the api container runs `--reload` with `./backend` mounted, so
  backend edits reload live — but a **new dependency** needs a rebuild.
- **Redis cache**: identical `(category, query)` is cached. `FLUSHALL` before
  re-testing prompt/query changes.
- **Config is `@lru_cache`d**: changing `.env` (e.g. rotating a key) needs
  `docker compose restart api` to take effect.
- **Access tokens are 15 min**: long manual/Playwright sessions need re-login.
- **Windows console** is cp1252 — non-ASCII in stdout can mojibake; prefer the app UI
  or files for verifying multilingual output.

## Committing

Each milestone is its own commit + push (see the git history). Backend and frontend
changes that form one feature go together. Commit messages avoid embedded double quotes
(PowerShell 5.1 mangles them in here-strings).
