# Data Model

Postgres 16 + pgvector. ORM in `backend/app/infra/models.py` (SQLAlchemy 2.0).
Migrations in `backend/migrations/versions/` (Alembic, run on API startup).

## Design principle

Per-category fields live in `items.metadata` (JSONB), so **adding a category needs no
schema change** — only a new ingestion adapter and a `categories` row. The search
pipeline and API are untouched (Open/Closed).

## Tables

### `users`
| Column | Type | Notes |
|---|---|---|
| id | int PK | |
| email | varchar(320) | unique, indexed |
| password_hash | varchar(255) | Argon2 |
| created_at | timestamptz | |

### `categories`
| Column | Type | Notes |
|---|---|---|
| id | int PK | |
| key | varchar(32) | unique — `movies`, `tv`, `songs`, `books`, `games`, `actors` |
| display_name | varchar(64) | |
| config_json | jsonb | icon, adapter |

### `items` — the catalog
| Column | Type | Notes |
|---|---|---|
| id | int PK | |
| category_id | FK → categories | indexed |
| external_id | varchar(128) | source id, or `gpt:<slug>` for free-form answers |
| title | varchar(512) | indexed |
| description | text | |
| metadata | jsonb | per-category fields (year, artist, `source`, …) |
| image_url / source_url | text | poster/cover + external link |
| created_at | timestamptz | |

Unique `(category_id, external_id)`. A **free-form** answer is materialized here as a
`gpt:<slug>` row with **no embedding**, so it's invisible to retrieval but still
saveable/votable.

### `item_embeddings` — the search index
| Column | Type | Notes |
|---|---|---|
| item_id | FK → items PK | cascade delete |
| embedding | vector(384) | bge-small-en-v1.5; **HNSW** index |
| search_tsv | tsvector | keyword index; **GIN** |

Both retrieval legs JOIN this table — which is *why* `gpt:*` rows (no embedding) are
auto-excluded from search.

### `searches`
| Column | Type | Notes |
|---|---|---|
| id | int PK | |
| user_id | FK → users (SET NULL) | indexed |
| category_id | FK → categories | |
| raw_query | text | |
| share_token | varchar(22) | unique, nullable — minted on demand |
| response_json | jsonb | full response snapshot (so shares/history render faithfully, incl. the free-form hero) |
| created_at | timestamptz | |

### `search_results`
| Column | Type | Notes |
|---|---|---|
| id | int PK | |
| search_id | FK → searches | cascade |
| item_id | FK → items | grounded results only |
| confidence | float | |
| rank | int | |
| reason | text | |

### `result_feedback`
| Column | Type | Notes |
|---|---|---|
| id | int PK | |
| user_id | FK → users (CASCADE) | |
| search_id | FK → searches (SET NULL) | only linked if owned by the voter |
| item_id | FK → items (CASCADE) | |
| vote | smallint | +1 / −1 |

Unique `(user_id, item_id)` — one vote per user per item (upsert).

### `collections` / `collection_items`
Named favourite lists. `collections` unique `(user_id, name)`; `collection_items`
unique `(collection_id, item_id)`. Both cascade on delete.

### `daily_challenges` / `challenge_attempts`
- `daily_challenges`: one row per `challenge_date` (unique), an `item_id`, and 3
  pre-generated `clues` (JSONB). The LLM writes clues once; every player reads the copy.
- `challenge_attempts`: unique `(user_id, challenge_id)`, tracking `guesses_used` and
  `solved`.

## Relationships (text ERD)

```
users 1─* searches 1─* search_results *─1 items *─1 categories
users 1─* collections 1─* collection_items *─1 items
users 1─* result_feedback *─1 items
users 1─* challenge_attempts *─1 daily_challenges *─1 items
items 1─1 item_embeddings
```

## Migration history

| Rev | Adds |
|---|---|
| `0001_initial` | users, categories, items, item_embeddings, searches, search_results + vector/tsvector indexes |
| `0002_collections` | collections, collection_items |
| `0003_feedback` | result_feedback |
| `0004_share` | searches.share_token, searches.response_json |
| `0005_challenge` | daily_challenges, challenge_attempts |

Migrations run automatically on API start (`alembic upgrade head` in the container
command). To run manually: `docker compose exec api alembic upgrade head`.
