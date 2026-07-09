# Overview

## The problem

Everyone has had a title on the tip of their tongue. *"That movie where twelve people
argue in one room about whether a kid is guilty."* You remember the **feeling** and a
few fragments, but not the name — so a normal search engine, which matches keywords,
fails. You don't know the keywords. You know the memory.

## The idea

MemoryLens takes that fuzzy fragment and returns the real title(s) it most likely
refers to, each with:

- a **confidence score** (a computed percentage, not a guess), and
- a plain-language **explanation** of why it matches your fragment.

The whole design rests on one principle:

> **Grounded RAG — the AI never invents titles.** It only ranks and explains items
> that were retrieved from a real catalog. If the answer isn't in the catalog, the
> system says so and clearly labels its world-knowledge guess.

This matters because a plain language model, asked "what movie is this?", will happily
hallucinate a confident, wrong, or non-existent title. MemoryLens constrains the model
to a real, category-filtered candidate list, so its answers stay trustworthy.

## The six categories

🎬 Movies · 📺 TV Series · 🎵 Songs · 📚 Books · 🎮 Games · 👤 Actors

You pick a category first. That choice becomes a **hard retrieval filter** — a Movies
search never touches Song rows. If your description clearly belongs elsewhere, the UI
offers a soft *"did you mean TV Series?"* nudge, but never switches on its own.

## How a search works (the 30-second version)

```
your memory  ─▶  clean & validate  ─▶  find candidates      ─▶  re-rank them
"twelve people                         (semantic + keyword       (a sharper model
 voting in                              search over the           reads query +
 one room"                              catalog, fused)           candidate together)
                                                                       │
   response  ◀── confidence % ◀── the LLM picks & explains ◀───────────┘
   (best match +   (computed from    the best matches from the
    alternatives)   real signals)     shortlist — it cannot add new titles
```

1. **Clean & validate** — trim the text, enforce length, strip any prompt-injection.
2. **Retrieve** — two searches run over the catalog in parallel: a *semantic* one
   (vector similarity, "means the same thing") and a *keyword* one ("shares words").
   Their rankings are fused.
3. **Rerank** — a heavier cross-encoder model re-scores the top candidates by reading
   your query and each candidate *together*, which is much sharper than the first pass.
4. **Reason** — the LLM receives the shortlist and picks/explains the best matches. It
   is told, firmly, that it may only choose from the given candidates.
5. **Confidence** — a score is *computed* by blending the LLM's rating, the rerank
   score, and the retrieval score. It is never just what the model claims.
6. **Fallbacks** — if no catalog item is a confident match, the LLM names the real
   title from its own knowledge (clearly marked "AI knowledge"). If the match is weak,
   it may attach one clarifying question to refine the search.

Steps 1–3 are **local, free, and deterministic** (they run on models inside the
container). Only step 4 hits the network, and it's a tiny, cheap model
(`gpt-4.1-nano`, ≈ $0.0003 per search).

## Why it's more than a demo

- **It's grounded** — real catalog data (TMDB, OpenLibrary, RAWG, iTunes), not vibes.
- **It's measured** — 92% top-1 accuracy on a fixed 48-query benchmark, with ablations
  showing what each component contributes ([RESULTS.md](../backend/eval/RESULTS.md)).
- **It's multilingual** — describe the memory in Azerbaijani, get an Azerbaijani answer.
- **It's a real product** — auth, history, collections, sharing, analytics, a daily
  guessing game, and a hardened, deployable stack. See [FEATURES.md](FEATURES.md).

Next: [ARCHITECTURE.md](../ARCHITECTURE.md) for the system design, or
[PIPELINE.md](PIPELINE.md) for the deep dive on the search itself.
