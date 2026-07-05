# Engagement on the free-form (AI knowledge) Best Match

**Date:** 2026-07-06
**Status:** Approved

## Problem

When the catalog has no confident match, the pipeline promotes a free-form
"gpt-knowledge" answer as the Best Match hero (`item_id=0`, generated live). That
hero is missing the actions every other card has:

- **Save to a collection** (`SaveButton`) — hidden because `item_id=0` has no
  catalog FK to reference.
- **👍/👎 feedback** (`FeedbackButtons`) — hidden for the same reason.
- **View source** — free-form answers have no `source_url`.

The user wants the AI Best Match to behave like the grounded cards.

Confirmed constraint: the AI answer is genuinely absent from the catalog (e.g.
"Mr. Robot" is not in the ~490-row tv catalog), so re-grounding it to an existing
row is not possible. The item must be given a real identity.

## Approach — Materialize the free-form answer as a lightweight catalog row

When `_identify_freeform` names a title, upsert a real `items` row for it and use
its real `id` as the result's `item_id`. Save/feedback then work through the
existing FK-based flow with no new tables.

Why this works cleanly:
- `Item.embedding` is optional; both retrieval legs `JOIN ItemEmbedding`
  (`retriever.py:85,105`), so a row **without** an embedding is automatically
  invisible to vector *and* keyword search — no exclusion filter needed. The
  materialized row is inert for grounding but usable for save/feedback/source.
- The `(category_id, external_id)` unique constraint (`models.py:52`) makes the
  upsert idempotent: repeated searches for the same AI title reuse one row, no
  duplicates.

Rejected alternative: separate title-based storage for saves/feedback — two code
paths, extra schema, more surface area. Not worth it.

## Changes

### Backend — `app/ai/pipeline.py`

- `_identify_freeform(category, query)` gains a `db: Session` parameter. Thread
  `db` through `run` → `_maybe_add_freeform` → `_identify_freeform` (all already
  have `db` in scope at `run`).
- After the LLM identifies a title, find-or-create an `Item`:
  - `external_id = "gpt:" + _slug(title)` where `_slug` lowercases, keeps
    `[a-z0-9]`, collapses runs to single `-`, trims, caps length (≤120) to stay
    within the `String(128)` column.
  - `title`, `description` (the existing free-form `description`), `image_url`
    (existing OMDb poster), `item_metadata = {"source": "gpt-knowledge",
    "detail": ident.detail}`, `source_url = _google_url(title, category)`.
  - Lookup by `(category_id, external_id)`; if found, refresh `image_url` when we
    now have one and it was null (poster backfill), else insert. `db.flush()` to
    get the id. Do **not** create an `ItemEmbedding`.
  - `_google_url(title, category)` →
    `https://www.google.com/search?q=` + `urllib.parse.quote_plus(f"{title} {category.display_name}")`.
- Build the `ResultItem` with `item_id=<real id>`, keeping
  `metadata.source="gpt-knowledge"` (drives the amber AI styling) and the
  Cyrillic-guarded `reason`.
- On any DB error creating the row, fall back to `item_id=0` + `source_url=None`
  (current behaviour) so search never fails on a materialize hiccup.

### Backend — `app/services/search_service.py`

- No functional change required: `item_id` is now real, so `_persist` stores the
  result normally. Keep the existing `item_id==0` skip as a safety net for the
  fallback path.

### Frontend — `frontend/src/components/ResultCard.tsx`

- Remove the `!byAI` guard on `SaveButton` (line ~49) and on `FeedbackButtons`
  (line ~122) so both render on the AI hero now that it has a real `item_id`.
- `View source` already renders whenever `result.source_url` is present, so the
  Google link appears automatically — no change.
- Keep the amber AI badge / ring styling (keyed on `byAI`). The hero `SaveButton`
  sits top-right; the hero uses `ConfidenceDial` on the left of the text column,
  so no overlap (the `pr-10` compact-meter fix is unaffected).

## Data / retrieval impact

The catalog accumulates on-demand `gpt:*` external rows. They carry no embedding
and no `search_tsv`, so they never surface as grounded candidates and never feed
"More like this" (`find_similar` returns `[]` without an embedding —
`retriever.py:22`). Deduped by `external_id`. Acceptable growth.

## Testing

**Backend (pytest, run via `backend/.venv`):**
- `_identify_freeform` creates an `Item` with the expected `external_id`,
  `source_url` (Google), `metadata.source="gpt-knowledge"`, and **no**
  `ItemEmbedding`; a second call with the same title reuses the same row (no
  duplicate).
- `_slug` slugifies/caps length correctly.
- A materialized `gpt:*` row is not returned by `HybridRetriever.search`
  (no embedding → excluded).
- Full suite stays green.

**Live (docker stack up, `redis-cli FLUSHALL`, Playwright), signed in:**
- Repeat the "hacker … rami malek" tv search → AI Best Match (Mr. Robot) hero
  shows: ✦ save, 👍/👎, and "View source ↗" (Google).
- Save it into a collection → appears on the Collections page.
- Vote 👍 → persists (feedback recorded, no error).
- Click View source → Google search for "Mr. Robot TV Series".
