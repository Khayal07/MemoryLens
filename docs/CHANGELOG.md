# Changelog

The build history of MemoryLens, oldest to newest. Grouped by phase; commit hashes in
parentheses. See `git log` for the full record.

## Foundation (Phases 0–8)

The core product, built in eight phases.

- **Phase 0 — Scaffold** (`a096638`): backend/frontend/infra skeleton, Docker Compose.
- **Phase 1 — Data model** (`9bd1436`): tables + initial migration; per-category JSONB.
- **Phase 2 — Ingestion + embeddings** (`7988f80`): catalog adapters, local bge embeddings.
- **Phase 3 — Retrieval** (`282437f`): hybrid pgvector + tsvector, RRF fusion, cross-encoder rerank.
- **Phase 4 — Reasoning** (`ec303c2`): LLM ranking/explanation, full pipeline, confidence.
- **Phase 5 — API + auth** (`1be42e5`): REST, JWT, history, rate limiting.
- **Phase 6 — Frontend SPA** (`4717911`): the "Lens/Recall" React app.
- **Phase 7 — Observability** (`c4b9cff`): structured logs, caching, readiness, metrics.
- **Phase 8 — CI** (`c2b267a`): GitHub Actions — backend lint+tests, frontend build.

## Real catalog & search quality

- Live OpenLibrary (books) + RAWG (games) adapters (`5fbd2d6`); 46 curated songs
  (`3fcef90`).
- Search quality: keyword OR, HyDE, weighted RRF, deeper rerank (`885a9c8`).

## AI upgrade & free-form fallback

- OpenAI `gpt-4.1-nano` primary with OpenRouter fallback (`0d1d2f8`).
- Free-form LLM fallback when the catalog match is weak (`0019421`), later made
  engageable — materialized, saveable, votable, sourced (`086067a`).
- Result visualization redesign: hero card, aperture dial, AI-knowledge badge (`3f0152d`).

## Frontend transformation

- Tailwind v4 + framer-motion, UI primitive library, premium layout, route
  code-splitting (`33660e4`→`9fb9666`).
- Aurora/glass visual system: living background, 3D tilt cards, glass surfaces,
  spatial page transitions (`3a9a3ba`→`1815b36`).

## Multilingual & correctness fixes

- Azerbaijani search (translate for retrieval, answer in-language) (`8f91c83`).
- Language-slip guards: no Russian/Portuguese drift (`7e7ff5f`, `bb426bb`).
- Grey-zone verification, category-instance answers, no blank reasons
  (`07f57de`, `b13255e`, `38203fa`).
- Free-form images for all six categories (OMDb/TMDB/iTunes/OpenLibrary/RAWG)
  (`88a0b85`, `3f1037d`, `3f6a14f`, `eb9d828`).

## Engagement features

- Similar items, collections, feedback loop, public share, analytics dashboard
  (`cb668c1`→`7d479d2`).

## The nine-feature batch

- Photo-develop poster reveal (`f5f962e`).
- Voice input with live waveform + silence auto-stop (`b7691d7`, `624db8d`).
- Multi-fragment recall board (`024c1b2`).
- Confidence breakdown rings that explain themselves (`5246517`→`455b91f`).
- Memory Lane — history as a poster timeline (`77d1106`).
- Memory Constellation — similarity star map with pan/zoom (`d94511c`, `a846406`).
- Akinator mode — one clarifying question (`3820173`).
- Daily challenge — three flipping clues (`e4f3541`).
- Cinematic scroll landing for signed-out visitors (`7bb9c85`).
- Duplicate-hero / rich-description / real-explanation fixes (`d6001de`).

## Evaluation & security (pre-deploy)

- **Retrieval benchmark** (`a780013`): 48-query dataset, recall@k/MRR harness, 6
  ablations. Retrieval 54% recall@1 vs full pipeline 92%. See
  [../backend/eval/RESULTS.md](../backend/eval/RESULTS.md).
- **Security hardening** (`368a316`→`4e1aa5d`): login-required search + per-user rate
  limit & daily quota, feedback IDOR fix, similar-items cap, JWT prod fail-fast,
  docs/metrics gating, security headers, production compose + non-root images. See
  [SECURITY.md](SECURITY.md).
- **Documentation**: this `docs/` set.
