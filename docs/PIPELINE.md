# The Search Pipeline

The heart of MemoryLens. Orchestrated by `backend/app/ai/pipeline.py`
(`SearchPipeline.run`). Every stage is swappable behind a port; the LLM only ever
ranks and explains real candidates.

```
validate → clean (+injection scrub) → [translate] → hybrid retrieve → rerank →
LLM reason → confidence + breakdown → free-form fallback → clarifying question → response
```

Stages before the LLM are **local, deterministic, and free**. Only reasoning (and the
optional HyDE/translate/free-form steps) call the network. On any LLM or parse failure,
the pipeline degrades gracefully to deterministic rerank order.

---

## 1. Validate & clean — `app/ai/cleaning.py`

- **Validate:** length must be 3–1000 characters (`MIN_LEN`/`MAX_LEN`), else `QueryError`.
- **Clean:** collapse whitespace, then **scrub prompt injection** — patterns like
  *"ignore previous instructions"*, *"system prompt"*, *"you are now"* are removed so a
  memory fragment can't hijack the reasoning step.

## 2. Translate (multilingual) — `pipeline._to_retrieval_query`

The local embedding and rerank models are English-only. A non-English memory (detected
by a non-ASCII regex, e.g. Azerbaijani `ə ğ ş ç ö ü ı`) is translated to English **for
retrieval only** (`ai/prompts/translate.py`). The **original** text still drives the LLM
reasoning, so answers come back in the user's language. Best-effort: an LLM failure
falls back to the raw query. Controlled by `TRANSLATE_ENABLED`.

## 3. HyDE query expansion (optional) — `pipeline._expand_query`

HyDE = *Hypothetical Document Embeddings*. The LLM writes a short hypothetical catalog
description of what the user is remembering; that text is embedded alongside the query
to sharpen the semantic leg. Off by default (`HYDE_ENABLED=false`) because it adds a
second LLM call — see the accuracy/latency trade-off in
[RESULTS.md](../backend/eval/RESULTS.md).

## 4. Hybrid retrieval — `app/ai/retriever.py`

Two independent searches over the catalog, **both hard-filtered by category**:

| Leg | How | Signal |
|-----|-----|--------|
| **Semantic (vector)** | pgvector cosine kNN over `item_embeddings.embedding` (bge-small-en, 384-dim) | "means the same thing" |
| **Keyword (lexical)** | Postgres `tsvector` full-text over `item_embeddings.search_tsv` | "shares actual words" |

A subtlety: the keyword leg **ORs** the query lexemes instead of ANDing them
(`plainto_tsquery` with `&`→`|`), because a long fuzzy memory almost never contains all
the exact catalog words — any matching clue should still surface a candidate
(`ts_rank` still rewards more overlap).

The two ranked lists are fused with **weighted Reciprocal Rank Fusion**
(`app/ai/fusion.py`), vector weighted 1.0 and keyword 0.6 (`RRF_VECTOR_WEIGHT` /
`RRF_KEYWORD_WEIGHT`). RRF is robust: it combines rankings without needing the two
scores to be on the same scale.

## 5. Rerank — `app/ai/reranker.py`

The bi-encoder retrieval above scores query and document *independently*. A
**cross-encoder** (`cross-encoder/ms-marco-MiniLM-L6-v2`, local) reads the
`(query, candidate)` pair *together*, which is far more precise — but expensive, so it
only runs on the fused top-N (`RERANK_TOP_N`, default 12). Output: the shortlist handed
to the LLM, best-first.

## 6. LLM reasoning — `app/ai/llm.py` + `app/ai/prompts/reasoning.py`

The LLM receives the category, the valid category keys, the memory, and the reranked
shortlist. It returns **strict JSON** (`app/ai/reasoning.py` parses it, with one repair
retry on malformed output) naming which candidates match, a per-match rating, a
one-line reason, and an optional category-mismatch suggestion.

Guardrails baked into the prompt:
- **Never invent an `item_id`** — only choose from the given candidates.
- **Explain, don't restate** — map each fragment to a concrete item fact the user did
  *not* mention; name the closest rejected alternative.
- **Answer in the memory's language** (a trailing reminder reinforces this).

**Provider chain** (`LLMClient`): OpenAI `gpt-4.1-nano` primary → OpenRouter free model
fallback on error (`LLM_FALLBACK_ENABLED`). On total failure the pipeline uses
deterministic rerank order with no reasons.

## 7. Confidence & breakdown — `app/ai/confidence.py`

The confidence percentage is **computed, never claimed**. It blends three signals:

- the LLM's match rating,
- `sigmoid(rerank_score)`,
- the retrieval score relative to the best in the set.

`compute_breakdown` returns the per-signal contribution in percentage points (summing
to the confidence) — `llm`, `rerank`, `retrieval` for grounded rows; `ai_knowledge` for
free-form; `feedback` when crowd votes nudged it; `ai_agreement` when a free-form answer
independently confirmed a grounded row. The UI renders this as concentric rings.

## 8. Free-form fallback — `pipeline._maybe_add_freeform`

The catalog can't contain everything (songs are a curated set of ~46). When the best
grounded confidence is below the floor (`FREEFORM_CONFIDENCE_FLOOR`, 65), the LLM names
the real title from world knowledge (`ai/identify.py`). That answer:

- becomes the **Best Match**, capped at 90% and marked `metadata.source="gpt-knowledge"`;
- is **materialized** as a lightweight catalog row (`gpt:<slug>`, no embedding so it
  stays out of retrieval) giving it a real `item_id` — so it can be saved, voted, shared;
- gets a real image from the right source per category (OMDb / TMDB / iTunes /
  OpenLibrary / RAWG);
- gets a rich 2–3 sentence catalog-style description.

**Grey zone** (`FREEFORM_GREY_MARGIN`, 8): a grounded match just above the floor is
still verified against the LLM's world-knowledge answer — the grounded pick is
overridden only when the LLM names a *different* title (`ai/matching.same_title`). If
they agree, the grounded row is promoted and its confidence lifted (`ai_agreement`), so
the same title is never shown twice.

## 9. Clarifying question (Akinator mode) — `pipeline._maybe_clarify`

When the final answer is still uncertain — a weak grounded top, or a free-form guess the
catalog doesn't corroborate — the LLM attaches **one** clarifying question
(`ai/clarify.py`). The frontend folds the user's answer back into a refined re-search
(up to two rounds). Suppressed when the match is confident or the catalog agrees with
the AI. Language-slip guarded.

## Cross-cutting guards

- **Language-slip scrubbing** (`pipeline._is_language_slip`): the small model sometimes
  drifts into Russian or Portuguese. A reply in a different script/language than the
  memory is blanked (the UI shows a neutral template), while a genuine in-language
  answer is kept.
- **Caching** (`app/infra/cache.py`): identical `(category, query)` fragments skip the
  whole pipeline within a Redis TTL. Feedback is re-applied on every request so votes
  take effect even on cache hits.

## Where to look

| Concern | File |
|---|---|
| Orchestration | `app/ai/pipeline.py` |
| Retrieval (vector + keyword) | `app/ai/retriever.py` |
| Fusion (RRF) | `app/ai/fusion.py` |
| Rerank | `app/ai/reranker.py` |
| Embeddings | `app/ai/embedder.py` |
| LLM client + provider chain | `app/ai/llm.py` |
| Prompts | `app/ai/prompts/` |
| Confidence | `app/ai/confidence.py` |
| Free-form identify | `app/ai/identify.py` |
| Title matching | `app/ai/matching.py` |
| Cleaning/validation | `app/ai/cleaning.py` |
