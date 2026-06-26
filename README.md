# MemoryLens

Find things you only partially remember. Describe a fragment — *"twelve people voting in one room"* — and MemoryLens returns the most likely real titles, grounded in a real catalog, with confidence scores and explanations.

> AI course final project, built as a production-grade SaaS.

## Categories (V1)

🎬 Movies · 📺 TV Series · 🎵 Songs · 📚 Books · 🎮 Games · 👤 Actors

The user picks a category first; it becomes a hard retrieval filter. The AI ranks and explains real candidates — it never invents titles. If a query clearly belongs to another category, the UI offers a soft "switch?" suggestion.

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI (Python 3.12) |
| Frontend | React + Vite + TypeScript |
| Store + Vectors | Postgres 16 + pgvector |
| Cache / rate-limit | Redis |
| Embeddings / rerank | sentence-transformers (local) |
| LLM reasoning | OpenRouter |
| Infra | Docker Compose, GitHub Actions |

## Architecture

```
React SPA → FastAPI (routers → services → AI pipeline)
                       ├─ Postgres + pgvector  (catalog, vectors, keyword)
                       ├─ Redis                (cache, rate limit)
                       └─ OpenRouter           (LLM reasoning only)
   local models: embeddings + cross-encoder reranking
```

Search pipeline: validate → clean → understand → hybrid retrieve (vector + keyword + RRF) → rerank → LLM reasoning → confidence → alternatives → response.

## Getting started

```bash
cp .env.example .env      # then fill OPENROUTER_API_KEY
docker compose up --build
```

- API: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Health: http://localhost:8000/health

## Status

🚧 Phase 0 — Foundation (scaffold). See the full roadmap in the architecture plan.
