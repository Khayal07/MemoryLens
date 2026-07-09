# Catalog & Ingestion

The catalog is the ground truth the AI is allowed to rank. Retrieval only ever returns
real rows from it — that's what "grounded" means.

## What's in it

| Category | Live source | Approx. rows | Notes |
|---|---|---|---|
| Movies | TMDB | ~490 | poster via TMDB, OMDb fallback |
| TV Series | TMDB | ~474 | |
| Actors | TMDB | ~496 | bios describe careers |
| Books | OpenLibrary | ~242 | keyless source |
| Games | RAWG | ~300 | needs a RAWG key |
| Songs | *fixtures only* | ~46 | curated with thematic descriptions |

Songs have **no live adapter**: free music-metadata APIs lack the thematic descriptions
that memory search needs, so songs ship as a curated fixture set (covers are still
backfilled from iTunes, keyless).

## Ingestion pipeline (`app/ingest/`)

```
fetch (adapter) → normalize → embed (bge-small-en) → upsert item + embedding + tsvector
```

- **Idempotent**: keyed by `(category_id, external_id)`, re-running **updates** rows
  instead of duplicating (`runner._upsert_item` uses Postgres `ON CONFLICT`).
- Each item's embedding **and** keyword `tsvector` are computed at ingest time and
  stored in `item_embeddings`, so a search is a pure DB read (`runner.py`).

### Adapters (`app/ingest/registry.py`)

| Source mode | Behaviour |
|---|---|
| `fixture` | Bundled data. Always works, no keys, no network. |
| `live` | The external API (TMDB / OpenLibrary / RAWG). |
| `auto` (default) | Live when usable (key present, or keyless like OpenLibrary), else fixtures. |

Adding a category = add an adapter here + a `categories` row; the runner and pipeline
don't change.

## Commands

Run inside the api container (`docker compose exec api ...`):

```bash
# Seed everything from bundled fixtures (recommended first run — no keys needed)
python -m scripts.ingest --all --source fixture

# Live ingest one category (needs the relevant API key)
python -m scripts.ingest --category movies --source live --limit 200

# Auto: live if a key is configured, else fixtures
python -m scripts.ingest --category books
```

### Cover / poster backfills

```bash
python -m scripts.backfill_posters       # OMDb posters for movies/tv rows missing one
python -m scripts.backfill_song_covers    # iTunes covers for catalog songs
```

## Gotcha

If an old ingest left **stale duplicates** (e.g. a title changed upstream), the unique
constraint is on `external_id`, not title — so a source that changes an item's id
creates a new row. Re-running `--source fixture` reconciles to the bundled set. When
testing prompt/query changes on a repeated query, remember search responses are cached
in Redis: `docker compose exec redis redis-cli FLUSHALL`.
