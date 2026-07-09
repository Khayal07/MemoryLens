# Features

Every user-facing capability. Backend service in parentheses; frontend page/component
where relevant.

## Core search

- **Grounded fuzzy search** — describe a memory, get ranked real titles with computed
  confidence and explanations (`search_service`, `Search.tsx`). See [PIPELINE.md](PIPELINE.md).
- **Six categories** as hard filters — Movies, TV, Songs, Books, Games, Actors
  (`CategorySelect.tsx`).
- **Confidence dial + breakdown** — a circular aperture shows the score; a toggle
  reveals the per-signal ring breakdown in plain words (`ConfidenceDial.tsx`,
  `ConfidenceBreakdown.tsx`).
- **Best Match hero + alternatives grid** — the top result is a large hero card; the
  rest sit in a responsive grid (`ResultCard.tsx`).
- **Category-mismatch nudge** — a soft "did you mean TV Series?" banner; never
  auto-switches (`MismatchBanner.tsx`).
- **Free-form (AI knowledge) answers** — when the catalog can't answer, the LLM names
  the real title, clearly badged, with a real poster/cover fetched live. Saveable and
  votable like any result.
- **Multilingual** — describe the memory in Azerbaijani, get an Azerbaijani answer.

## Input modes

- **Voice input** — Web Speech dictation with a live waveform, EN/AZ toggle, and a
  5-second silence auto-stop (`VoiceInput.tsx`).
- **Fragment board** — enter clues as chips that fly toward the lens while the search
  runs (`FragmentBoard.tsx`).
- **Akinator clarify** — on a weak match, the app asks one refining question and folds
  the answer back into the search, up to two rounds (`ClarifyBubble.tsx`).

## Accounts & saving

- **Auth** — email/password register, login, refresh, `/me` (Argon2 + JWT).
- **History** — every search, with a best-match thumbnail; list or **Memory Lane**
  timeline view with a scroll-snap poster strip (`History.tsx`, `MemoryLane.tsx`).
- **Collections** — named favourite lists; create, rename, delete, add/remove items
  (`collections_service`, `Collections.tsx`, `SaveButton.tsx`).
- **Similar items** — "more like this" catalog neighbours under a grounded result
  (`retriever.find_similar`, `SimilarItems.tsx`).

## Social & insight

- **Feedback** — 👍/👎 a result; votes nudge future confidence (`feedback_service`,
  `FeedbackButtons.tsx`).
- **Public share** — mint a read-only link to a search that renders the full snapshot,
  including a free-form hero (`share_service`, `ShareButton.tsx`, `SharedResult.tsx`).
- **Analytics** — a usage dashboard: totals, last-7-days, avg confidence, grounded vs
  free-form, votes, by-category bars, top queries (`analytics_service`, `Analytics.tsx`).
- **Constellation** — the user's found/saved items as an interactive similarity star
  map with pan/zoom (`constellation_service`, `Constellation.tsx`).

## Play

- **Daily challenge** — one secret catalog item per day, revealed by three
  progressively flipping clues; three fuzzy guesses, wrong-guess shake, emoji share
  card on solve (`challenge_service`, `Challenge.tsx`).

## Presentation

- **Cinematic landing** — signed-out visitors get a four-scene scroll-driven story
  (aperture rings open, memory sentence types itself, category chips orbit in, glass
  CTA); signed-in users land on the category grid (`Landing.tsx`, `HomeGate`).
- **Aurora / glass UI** — drifting blurred orbs behind frosted-glass surfaces, 3D tilt
  cards, spring animations, photo-develop image reveals; respects reduced-motion
  (`AuroraBackground.tsx`, `TiltCard.tsx`, framer-motion).

## Operations

- **Health & readiness** — `/health`, `/readyz` (checks Postgres + Redis).
- **Observability** — structured JSON logs with request IDs, Prometheus `/metrics`.
- **Rate limiting & quotas** — per-user search burst + daily cap; per-IP auth limit.
- **Caching** — identical fragments skip the pipeline within a Redis TTL.
