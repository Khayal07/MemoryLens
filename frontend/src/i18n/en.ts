// English strings. Keys are dotted paths; `{var}` marks an interpolation slot.
// az.ts must mirror this key set. Missing keys fall back here (see LanguageContext).
export const en: Record<string, string> = {
  // common
  "common.back": "Back",
  "common.loading": "Loading…",
  "common.done": "Done",
  "common.cancel": "Cancel",
  "common.save": "Save",
  "common.viewSource": "View source ↗",
  "common.startRecalling": "Start recalling →",
  "common.genericError": "Something went wrong.",

  // language toggle
  "lang.aria": "Switch language",
  "lang.en": "EN",
  "lang.az": "AZ",

  // nav / layout
  "nav.collections": "Collections",
  "nav.history": "History",
  "nav.analytics": "Analytics",
  "nav.constellation": "Constellation",
  "nav.daily": "Daily",
  "nav.signOut": "Sign out",
  "nav.signIn": "Sign in",
  "nav.createAccount": "Create account",
  "nav.menu": "Menu",
  "nav.skip": "Skip to content",
  "nav.home": "MemoryLens home",

  // category select
  "category.eyebrow": "Half-remembered? Start here",
  "category.title1": "You almost have it.",
  "category.title2": "Bring it into focus.",
  "category.subtitle":
    "Describe the fragment you remember — we search a real catalog and surface the most likely match, with how sure we are and why.",
  "category.errorTitle": "Couldn't load categories.",
  "category.errorHint": "Is the API running? Try refreshing in a moment.",
  "category.searchThis": "Search this category",
  "category.name.movies": "Movies",
  "category.name.tv": "TV Series",
  "category.name.songs": "Songs",
  "category.name.books": "Books",
  "category.name.games": "Games",
  "category.name.actors": "Actors",
  "category.desc.movies": "A scene, a single room, a face you can't place",
  "category.desc.tv": "That show with the thing that happened",
  "category.desc.songs": "A lyric, a mood, rain on the chorus",
  "category.desc.books": "Dragons, a title just out of reach",
  "category.desc.games": "Yellow hair, a level you replayed for years",
  "category.desc.actors": "Always the villain, never the name",

  // auth
  "auth.login.title": "Welcome back",
  "auth.login.subtitle": "Sign in to keep your search history.",
  "auth.login.submit": "Sign in",
  "auth.login.busy": "Signing in…",
  "auth.login.footerPre": "New here?",
  "auth.login.footerLink": "Create an account",
  "auth.login.failed": "Sign in failed.",
  "auth.register.title": "Create account",
  "auth.register.subtitle": "Save every search and pick up where you left off.",
  "auth.register.submit": "Create account",
  "auth.register.busy": "Creating…",
  "auth.register.short": "Password must be at least 8 characters.",
  "auth.register.footerPre": "Already have one?",
  "auth.register.footerLink": "Sign in",
  "auth.register.failed": "Could not create account.",
  "auth.field.email": "Email",
  "auth.field.password": "Password",

  // search
  "search.allCategories": "← All categories",
  "search.placeholder": "Describe the {category} you half-remember…",
  "search.ariaDescribe": "Describe what you remember",
  "search.fragmentPlaceholder": "Drop the first fragment you remember…",
  "search.hintFragments": "Enter adds a fragment · Recall searches them all together",
  "search.hintText": "Press Enter to search · Shift+Enter for a new line",
  "search.focusing": "Focusing…",
  "search.recall": "Recall",
  "search.toFreeText": "Switch to free text",
  "search.toFragment": "Switch to fragment mode",
  "search.freeTextTitle": "Free text",
  "search.fragmentsTitle": "Fragments",
  "search.bestMatch": "Best match",
  "search.otherPossibilities": "Other possibilities",
  "search.nothingMatched": "Nothing matched in {category}.",
  "search.nothingHint": "Try more details — a scene, a character, a feeling.",
  "search.ex.movies.1": "Twelve people arguing in one room over a verdict",
  "search.ex.movies.2": "A man plants an idea inside a dream",
  "search.ex.tv.1": "A chemistry teacher starts cooking drugs",
  "search.ex.tv.2": "Kids and a monster from another dimension",
  "search.ex.songs.1": "A man singing about walking in the rain",
  "search.ex.songs.2": "An operatic rock song about killing a man",
  "search.ex.books.1": "A hobbit, a dragon, and a stolen treasure",
  "search.ex.books.2": "A boy finds a dragon egg and learns magic",
  "search.ex.games.1": "A blue hedgehog collecting rings at high speed",
  "search.ex.games.2": "A hero with a sword saving a princess in an open world",
  "search.ex.actors.1": "He always plays mafia and crime bosses",
  "search.ex.actors.2": "The actor from Titanic and Inception",

  // result card
  "result.aiKnowledge": "✦ AI knowledge",
  "result.why": "why?",
  "result.whyAria": "Why this confidence? Toggle the signal breakdown",

  // clarify
  "clarify.oneMore": "One more detail",
  "clarify.answerPlaceholder": "Your answer…",
  "clarify.answerAria": "Answer the clarifying question",
  "clarify.refine": "Refine ↺",

  // mismatch
  "mismatch.looksLike": "This looks more like {category}.",
  "mismatch.switchTo": "Switch to {category}",

  // save
  "save.aria": "Save to a collection",
  "save.saveTo": "Save to",
  "save.noCollections": "No collections yet.",
  "save.newCollection": "New collection…",
  "save.add": "Add",

  // feedback
  "feedback.rateAria": "Rate this match",
  "feedback.good": "Good match?",
  "feedback.goodAria": "Good match",
  "feedback.badAria": "Bad match",

  // share
  "share.copied": "Link copied!",
  "share.creating": "Creating…",
  "share.share": "Share",
  "share.prompt": "Copy this share link:",

  // similar
  "similar.moreLikeThis": "More like this",

  // voice
  "voice.english": "English",
  "voice.azerbaijani": "Azerbaijani",
  "voice.langAria": "Speech language: {lang} — click to switch",
  "voice.stopAria": "Stop voice input",
  "voice.speakAria": "Speak your memory",

  // fragment board
  "fragment.addAnother": "Add another fragment…",
  "fragment.removeAria": "Remove fragment: {f}",
  "fragment.addAria": "Add a memory fragment",

  // confidence
  "confidence.inFocus": "in focus",
  "confidence.coming": "coming into focus",
  "confidence.fuzzy": "still fuzzy",
  "confidence.focusingLower": "focusing…",
  "confidence.ariaValue": "Confidence {pct} percent",

  // breakdown
  "breakdown.sumMany":
    "The {total}% is the sum of {n} independent signals — no single one can dominate:",
  "breakdown.sumOne": "Where this {total}% comes from:",
  "breakdown.llm.label": "AI judgement",
  "breakdown.llm.desc": "How strongly the AI rates this item as the match for your memory.",
  "breakdown.rerank.label": "Relevance match",
  "breakdown.rerank.desc":
    "A cross-checking model compares your words against this item's description.",
  "breakdown.retrieval.label": "Catalog retrieval",
  "breakdown.retrieval.desc": "How high this item surfaced when searching the catalog itself.",
  "breakdown.feedback.label": "Community votes",
  "breakdown.feedback.desc": "Thumbs up/down from users nudge the score over time.",
  "breakdown.ai_knowledge.label": "AI world knowledge",
  "breakdown.ai_knowledge.desc":
    "This answer isn't in our catalog — the AI named it from its own knowledge of the real world. Because we can't verify it against catalog data, confidence is capped at 90%.",

  // landing
  "landing.sentence": "twelve angry people arguing in one room over a verdict…",
  "landing.scrollHint": "scroll to focus ↓",
  "landing.youType": "You type what you remember",
  "landing.findsReal": "…and it finds the real thing",
  "landing.movieDesc":
    "A jury of twelve locked in one sweltering room, one holdout voting not guilty.",
  "landing.s3.title": "Six shelves of half-memories.",
  "landing.s3.subtitle": "Real catalogs — no invented answers. Pick a shelf and describe the fragment.",
  "landing.s4.title": "That thing on the tip of your tongue?",
  "landing.s4.subtitle":
    "Create an account to keep every find — history, collections, your memory constellation, and a daily guessing challenge.",
  "landing.s4.signIn": "Sign in ↗",

  // collections
  "collections.eyebrow": "Saved",
  "collections.title": "Your collections",
  "collections.createPlaceholder": "Create a new collection…",
  "collections.create": "Create",
  "collections.loadError": "Couldn't load your collections.",
  "collections.emptyTitle": "No collections yet.",
  "collections.emptyHint": "Search, then tap ✦ on a result to save it here.",
  "collections.rename": "Rename",
  "collections.delete": "Delete",
  "collections.empty": "Empty — save results here with ✦.",
  "collections.removeAria": "Remove {title}",

  // history
  "history.eyebrow": "Your searches",
  "history.title": "What you've looked for",
  "history.viewAria": "History view",
  "history.lane": "◧ Memory Lane",
  "history.list": "☰ List",
  "history.loadError": "Couldn't load your history.",
  "history.emptyTitle": "No searches yet.",
  "history.results": "{count} results",
  "history.timelineAria": "Search timeline",
  "history.bestAria": "{query} — best match {title}",
  "history.unknown": "unknown",

  // analytics
  "analytics.eyebrow": "Usage",
  "analytics.title": "Analytics",
  "analytics.loadError": "Couldn't load analytics.",
  "analytics.total": "Total searches",
  "analytics.last7": "Last 7 days",
  "analytics.avgConfidence": "Avg confidence",
  "analytics.grounded": "Grounded",
  "analytics.byCategory": "Searches by category",
  "analytics.feedback": "Feedback",
  "analytics.upvotes": "👍 Upvotes",
  "analytics.downvotes": "👎 Downvotes",
  "analytics.topQueries": "Top queries",
  "analytics.noSearches": "No searches yet.",
  "analytics.noData": "No data yet.",

  // constellation
  "constellation.eyebrow": "Your sky",
  "constellation.title": "Memory Constellation",
  "constellation.subtitle":
    "Every find becomes a star — colour is its category, size how often it surfaced, lines link memories that feel alike. Lone stars are AI-named finds outside the catalog.",
  "constellation.loadError": "Couldn't chart your constellation.",
  "constellation.emptyTitle": "No stars yet.",
  "constellation.emptyHint": "Search for a few memories and they'll appear here.",
  "constellation.mapAria": "Star map of your found items",
  "constellation.zoomIn": "Zoom in",
  "constellation.zoomOut": "Zoom out",
  "constellation.reset": "Reset view",
  "constellation.seen": "seen ×{n}",

  // challenge
  "challenge.daily": "Daily challenge #{n}",
  "challenge.category": "Category:",
  "challenge.title": "Guess today's secret from the clues.",
  "challenge.locked": "A wrong guess reveals the next clue.",
  "challenge.lockedAria": "Locked clue",
  "challenge.guessPlaceholder": "Your guess — a {category} title…",
  "challenge.guessAria": "Your guess",
  "challenge.checking": "Checking…",
  "challenge.guessN": "Guess {n}/{limit}",
  "challenge.notIt": "Not it — a new clue just flipped in.",
  "challenge.solvedIn": "Solved in {n}/{limit}",
  "challenge.outOfGuesses": "Out of guesses",
  "challenge.solvedMsg": "Sharp recall — the aperture snapped right into focus.",
  "challenge.failedMsg": "It slipped away today. Tomorrow brings a fresh secret.",
  "challenge.copied": "Copied ✓",
  "challenge.shareResult": "Share result",
  "challenge.unavailable": "Challenge unavailable.",

  // shared result
  "shared.unavailableTitle": "This shared recall isn't available.",
  "shared.unavailableHint": "The link may be wrong or the search was removed.",
  "shared.tryLink": "Try MemoryLens →",
  "shared.eyebrow": "Shared recall",
  "shared.noMatches": "No matches were found for this recall.",
  "shared.recallOwn": "Recall your own memory →",
};
