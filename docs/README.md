# MemoryLens — Documentation

Everything about the project, top to bottom. Start here.

> **MemoryLens** turns a fuzzy memory — *"twelve people voting in one room"* — into
> real, grounded matches with a confidence score and an explanation. It never invents
> titles: the LLM only ranks and explains candidates retrieved from a real catalog.

## Read in this order

| # | Document | What's inside |
|---|----------|---------------|
| 1 | [OVERVIEW.md](OVERVIEW.md) | The problem, the core idea (grounded RAG), and how a search flows end to end — in plain language. |
| 2 | [../ARCHITECTURE.md](../ARCHITECTURE.md) | The system diagram, layering, and where each responsibility lives. |
| 3 | [PIPELINE.md](PIPELINE.md) | The AI search pipeline, stage by stage: clean → retrieve → rerank → reason → confidence → free-form → clarify. |
| 4 | [DATA-MODEL.md](DATA-MODEL.md) | Every table, relationship, index, and the migration history. |
| 5 | [API.md](API.md) | Full REST reference — every endpoint, auth, request/response shapes, limits. |
| 6 | [FEATURES.md](FEATURES.md) | Every user-facing feature and how it works. |
| 7 | [CATALOG.md](CATALOG.md) | Where the catalog data comes from and how to (re)ingest it. |
| 8 | [CONFIGURATION.md](CONFIGURATION.md) | Every environment variable, with defaults and effects. |
| 9 | [DEVELOPMENT.md](DEVELOPMENT.md) | Local setup, project layout, testing, and the hard-won gotchas. |
| 10 | [SECURITY.md](SECURITY.md) | The threat model, the pre-deploy hardening, and the audit findings. |
| 11 | [CHANGELOG.md](CHANGELOG.md) | The full build history, phase by phase. |

## Quick facts

| | |
|---|---|
| **What** | AI search for half-remembered movies, TV, songs, books, games, actors |
| **Approach** | Grounded RAG — hybrid retrieval + cross-encoder rerank + LLM ranking/explanation |
| **Stack** | FastAPI · React/Vite/TS · Postgres+pgvector · Redis · OpenAI (fallback OpenRouter) · local sentence-transformers |
| **Accuracy** | 92% recall@1 (full pipeline) on a 48-query benchmark — see [../backend/eval/RESULTS.md](../backend/eval/RESULTS.md) |
| **Run** | `docker compose up --build` — see [../README.md](../README.md) |
| **Tests** | 188 backend tests (`backend/.venv/Scripts/python -m pytest`) |
| **Repo** | https://github.com/Khayal07/MemoryLens |

## Also in the repo

- [../README.md](../README.md) — run instructions, evaluation summary, production deploy.
- [../backend/eval/RESULTS.md](../backend/eval/RESULTS.md) — the accuracy benchmark and ablations.
- [superpowers/specs/](superpowers/specs/) — design specs kept from the build.
