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

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

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

## Status

✅ Backend (grounded RAG pipeline, hybrid retrieval, auth, history), frontend SPA
(Aurora + glass UI, Tailwind v4, framer-motion), 6 live categories with real
catalog data, observability, Docker, CI. Verified end-to-end.

**Repo:** https://github.com/Khayal07/MemoryLens
