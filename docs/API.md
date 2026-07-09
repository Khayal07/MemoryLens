# REST API Reference

Base path: **`/api/v1`**. All bodies are JSON. Interactive docs (development only):
`http://localhost:8000/docs`.

## Conventions

- **Auth**: send `Authorization: Bearer <access_token>`. Access tokens live 15 min;
  refresh tokens 7 days. Get them from `/auth/register` or `/auth/login`.
- **Errors**: a consistent envelope — `{"error": {"code": "...", "message": "..."}}`.
  Codes: `bad_request` (400), `unauthorized` (401), `not_found` (404), `conflict`
  (409), `validation_error` (422), `rate_limited` (429).
- **Rate limits**: auth endpoints 20/min per IP; `/search` per-user (see below).

Legend: 🔓 public · 🔒 requires access token.

---

## Auth — `/api/v1/auth`

| Method | Path | Auth | Body | Returns |
|---|---|---|---|---|
| POST | `/register` | 🔓 | `{email, password}` (password 8–128) | `201` `TokenResponse` |
| POST | `/login` | 🔓 | `{email, password}` | `TokenResponse` |
| POST | `/refresh` | 🔓 | `{refresh_token}` | `TokenResponse` (new pair) |
| GET | `/me` | 🔒 | — | `{id, email}` |

`TokenResponse` = `{access_token, refresh_token, token_type:"bearer"}`.
The whole router is rate-limited to 20 requests/min per IP.

---

## Search — `/api/v1`

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/search` | 🔒 | Run a search. Paid LLM call — see limits below. |
| GET | `/searches` | 🔒 | The caller's search history (latest 50). |
| POST | `/searches/{id}/share` | 🔒 | Mint (idempotent) a public share token for own search. |
| GET | `/share/{token}` | 🔓 | Fetch a shared search snapshot (read-only). |

**`POST /search`** — body `{category, query}` (query 3–1000 chars).
Returns `SearchResponse`:

```jsonc
{
  "query": "twelve jurors argue in a hot room",
  "category": "movies",
  "search_id": 1234,
  "results": [
    {
      "item_id": 42,
      "title": "12 Angry Men",
      "description": "…",
      "image_url": "https://…",
      "source_url": "https://…",
      "metadata": {},                 // internal keys (source/image_url) hidden by UI
      "confidence": 92.0,             // computed 0–100, not the model's claim
      "reason": "A jury deliberates a murder verdict in a single room…",
      "breakdown": {"llm": 40.1, "rerank": 30.5, "retrieval": 21.4},
      "confidence_note": null         // free-form answers explain their own confidence
    }
    // …alternatives
  ],
  "suggestion": null,                 // soft "did you mean <category>?" nudge, or null
  "clarifying_question": null         // Akinator mode: one refining question, or null
}
```

**Rate limits on `/search`** (why login is required — every request maps to a user we
can bill and cap):
- **Burst**: `SEARCH_RATE_PER_MIN` requests/min per user (default 10) → `429`.
- **Daily**: `SEARCH_DAILY_QUOTA` searches/day per user (default 50) → `429`.

Free-form (world-knowledge) best matches carry `metadata.source == "gpt-knowledge"`.

---

## Items — `/api/v1`

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/items/{item_id}/similar` | 🔓 | Catalog neighbours ("more like this"). `?limit=` 1–50 (default 6). |

Returns a list of `SimilarItem` = `{item_id, title, description, image_url, source_url, metadata}`.

---

## Collections (favourites) — `/api/v1`

All 🔒 and owner-scoped.

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/collections` | — | `CollectionOut[]` (with items) |
| POST | `/collections` | `{name}` (1–80) | `201` `CollectionOut` (409 on dup name) |
| PATCH | `/collections/{id}` | `{name}` | `CollectionOut` (rename) |
| DELETE | `/collections/{id}` | — | `204` |
| POST | `/collections/{id}/items` | `{item_id}` | `204` (add) |
| DELETE | `/collections/{id}/items/{item_id}` | — | `204` (remove) |

`CollectionOut` = `{id, name, created_at, items: SavedItem[]}`;
`SavedItem` = `{item_id, title, description, image_url, source_url, category, metadata}`.

---

## Feedback — `/api/v1`

| Method | Path | Auth | Body |
|---|---|---|---|
| POST | `/feedback` | 🔒 | `{search_id?, item_id, vote}` where `vote ∈ {-1, 1}` → `204` |

Upserts one vote per `(user, item)`. A `search_id` is only linked when it belongs to
the voting user (else detached). Votes nudge grounded confidence ±8 pts on future
searches (`feedback_service.apply_feedback`).

---

## Analytics — `/api/v1`

| Method | Path | Auth | Returns |
|---|---|---|---|
| GET | `/analytics` | 🔒 | `AnalyticsOverview` (global usage) |

`AnalyticsOverview` = totals, `searches_last_7d`, `avg_confidence`, grounded vs
free-form counts, up/downvotes, `by_category[]`, `top_queries[]`.

---

## Constellation — `/api/v1`

| Method | Path | Auth | Returns |
|---|---|---|---|
| GET | `/constellation` | 🔒 | `{nodes[], edges[]}` |

The caller's searched + saved items as a similarity star map. Nodes cap at 60; edges
connect items with pairwise embedding cosine ≥ 0.55 (top-3 per node). Free-form (`gpt:*`)
rows float unlinked (no embedding).

---

## Daily Challenge — `/api/v1`

Both 🔒.

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/challenge/today` | — | `ChallengeState` |
| POST | `/challenge/guess` | `{guess}` (1–200) | `ChallengeState` (422 if finished) |

`ChallengeState` = `{number, date, category, clues[], clues_total, guesses_used,
guess_limit, solved, finished, correct?, answer?}`. Clues are gated: you only see the
ones you've earned (guesses_used + 1). The `answer` is revealed only when finished
(solved or out of 3 guesses). Guess matching is fuzzy (`ai/matching.same_title`).

---

## Categories & health — `/api/v1`

| Method | Path | Auth | Returns |
|---|---|---|---|
| GET | `/categories` | 🔓 | `[{key, display_name, config}]` |
| GET | `/health` | 🔓 | `{status:"ok"}` (liveness) |
| GET | `/readyz` | 🔓 | `{status, checks:{db, redis}}` — `503` if a dependency is down |
| GET | `/metrics` | 🔓/🔒 | Prometheus metrics. Gated by `X-Metrics-Token` header when `METRICS_TOKEN` is set (production). |

> In **production** (`ENV != development`), `/docs`, `/redoc`, and `/openapi.json` are
> disabled, and `/metrics` requires the token.
