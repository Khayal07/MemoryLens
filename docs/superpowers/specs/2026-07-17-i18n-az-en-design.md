# MemoryLens — Azerbaijani / English language support

**Date:** 2026-07-17
**Status:** Approved (design)

## Problem & goal

The UI chrome is English-only. Search *answers* already come back in the memory's
detected language, but the buttons, labels, headings, placeholders and empty states are
always English, and a user can't choose. Goal: a first-class **AZ / EN language switch**
where the selected language drives **everything** — the whole UI *and* the AI answers.

**User decisions:**
- Default on first visit: **auto-detect** from the browser (`az` if the browser language
  starts with `az`, else `en`), then persisted.
- The selected language controls **both** UI chrome and answer language: pick AZ → every
  label and every AI explanation is Azerbaijani, no matter what language the user typed.

## Non-goals

- Fixing the AZ→EN *retrieval* translation quality (e.g. "səs verir" = _to vote_ being
  mistranslated as _to make a sound_). That derails which catalog rows are retrieved and
  is a separate quality bug in the translate prompt — noted as a follow-up, not this work.
- A third language. The design keeps a dictionary-per-language shape so adding one later
  is mechanical, but only `en` + `az` ship now.

## Architecture

### Frontend — UI translation (dependency-light, matches the existing custom setup)

- New `frontend/src/i18n/`:
  - `en.ts`, `az.ts` — flat/nested string dictionaries keyed by dotted paths
    (`nav.collections`, `search.recall`, `landing.hero.title`, …). Same key set in both.
  - `types.ts` — a `Lang = "en" | "az"` type and the dictionary shape (typed off `en`).
  - `LanguageContext.tsx` — `LanguageProvider` + `useI18n()` exposing `{ lang, setLang,
    t }`. `t(key, vars?)` resolves the dotted key in the active dictionary, does simple
    `{var}` interpolation, and falls back to the `en` value then the raw key if missing.
  - Init order: `localStorage["memorylens.lang"]` → else
    `navigator.language.toLowerCase().startsWith("az") ? "az" : "en"`. On `setLang`:
    persist to localStorage and set `document.documentElement.lang`.
- `LanguageProvider` wraps the app in `main.tsx` (outside the router, alongside the
  existing providers).
- A **language toggle** (`AZ | EN` segmented control) in `Layout.tsx`, shown in both the
  desktop nav and the mobile hamburger panel, for signed-in and signed-out states.
- Every hardcoded English string in `pages/` and `components/` is replaced with
  `t("...")`. This is the bulk of the work (~25 files). Dynamic/interpolated strings use
  `t("key", { name })`. Aria-labels and placeholders are translated too.

### Backend — answer language

- `SearchRequest` (schemas/search.py) gains `language: str | None = None` (accepts
  `"az"` / `"en"`; anything else treated as `None`). The frontend sends the active `lang`
  on every `/search`.
- `search_service.run_search(db, category, query, user_id, language)` threads it into the
  pipeline and the cache key.
- `SearchPipeline.run(db, category_key, query, max_results, language=None)`:
  - Passes an explicit target language into the reasoning / identify / clarify prompt
    builders. Each prompt currently says "answer in the memory's language"; it gains an
    optional directive: when `language` is set, "write `reason` / `message` /
    `description` / `question` in **Azerbaijani** (or **English**)", overriding detection.
    When `language is None`, behaviour is unchanged (detect from the memory).
  - Retrieval's AZ→EN translation (`_to_retrieval_query`) is **unchanged** — the local
    embed/rerank models stay English-only.
- **Language-slip guard** (`_is_language_slip`): today it scrubs a non-ASCII reply to an
  ASCII (English) memory. With an explicit `language="az"`, an Azerbaijani reply to an
  English memory is *intended*, so the guard must not scrub it. Thread the target language
  in: only scrub Cyrillic-to-non-Cyrillic and non-ASCII-to-ASCII **when the caller did not
  force AZ**. A forced-EN answer that comes back non-ASCII is still a slip and scrubbed.
- **Cache** (infra/cache.py): key becomes `(category, query, language)` so AZ and EN
  answers to the same query are stored separately. Existing calls default `language=None`.

## Data flow

User toggles AZ → `setLang("az")` → localStorage + context re-render (all `t()` → AZ) →
every `/search` body includes `language:"az"` → pipeline forces AZ in the answer prompts,
slip-guard permits AZ → response cached under `(category, query, "az")` → hero/reason/
clarify all render Azerbaijani.

## Testing

- **Backend** (pytest, keep all green):
  - `SearchRequest` parses/normalizes `language`.
  - `run_search` / pipeline pass `language` through; cache key includes it (AZ and EN
    don't collide).
  - Prompt builders include the language directive when given one; omit it when `None`.
  - `_is_language_slip` relaxed: AZ reply + forced-AZ ⇒ kept; forced-EN + non-ASCII ⇒
    scrubbed; `None` ⇒ current behaviour.
- **Frontend**: `npm run build` (tsc) clean; Playwright smoke — toggle flips nav labels
  EN↔AZ, and an AZ search returns an Azerbaijani reason.

## Files touched (representative)

- Frontend: `src/i18n/{en,az,types}.ts`, `src/i18n/LanguageContext.tsx`, `src/main.tsx`,
  `src/components/Layout.tsx`, and every `src/pages/*` + `src/components/*` with literal
  copy; `src/lib/api.ts` (send `language` on search).
- Backend: `app/schemas/search.py`, `app/services/search_service.py`, `app/ai/pipeline.py`,
  `app/ai/prompts/{reasoning,identify,clarify}.py`, `app/infra/cache.py`.
