"""Live OpenLibrary adapter (books) — keyless. Pulls highly-rated works across a
spread of popular subjects and builds an embedding-friendly description from the
first sentence + subjects, since memory fragments are usually about plot/themes."""

from collections.abc import Iterable

import httpx

from app.ingest.base import NormalizedItem

SEARCH_URL = "https://openlibrary.org/search.json"
COVER_URL = "https://covers.openlibrary.org/b/id/{cover}-M.jpg"

# Breadth across the subjects people most often half-remember.
SUBJECTS = [
    "fantasy",
    "science_fiction",
    "mystery",
    "thriller",
    "romance",
    "horror",
    "historical_fiction",
    "adventure",
    "young_adult",
    "classic_literature",
]
FIELDS = "key,title,author_name,first_publish_year,cover_i,subject,first_sentence"


class OpenLibraryAdapter:
    category_key = "books"

    def fetch(self, limit: int = 500) -> Iterable[NormalizedItem]:
        per_subject = max(20, limit // len(SUBJECTS))
        seen: set[str] = set()
        count = 0
        with httpx.Client(timeout=30.0, headers={"User-Agent": "MemoryLens/0.1"}) as client:
            for subject in SUBJECTS:
                if count >= limit:
                    break
                resp = client.get(
                    SEARCH_URL,
                    params={
                        "subject": subject,
                        "limit": per_subject,
                        "sort": "rating",
                        "fields": FIELDS,
                    },
                )
                resp.raise_for_status()
                for doc in resp.json().get("docs", []):
                    if count >= limit:
                        break
                    item = self._normalize(doc, subject, seen)
                    if item:
                        yield item
                        count += 1

    def _normalize(self, doc: dict, subject: str, seen: set[str]) -> NormalizedItem | None:
        key = doc.get("key")
        title = doc.get("title")
        if not key or not title or key in seen:
            return None
        seen.add(key)

        authors = doc.get("author_name") or []
        subjects = (doc.get("subject") or [])[:5]
        first_sentence = doc.get("first_sentence")
        if isinstance(first_sentence, list):
            first_sentence = first_sentence[0] if first_sentence else None

        parts: list[str] = []
        if first_sentence:
            parts.append(str(first_sentence))
        parts.append(
            f"A {subject.replace('_', ' ')} book"
            + (f" by {authors[0]}" if authors else "")
            + "."
        )
        if subjects:
            parts.append("Themes: " + ", ".join(subjects) + ".")

        cover = doc.get("cover_i")
        return NormalizedItem(
            external_id=f"ol:{key}",
            title=title,
            description=" ".join(parts),
            image_url=COVER_URL.format(cover=cover) if cover else None,
            source_url=f"https://openlibrary.org{key}",
            metadata={
                "author": authors[0] if authors else None,
                "year": doc.get("first_publish_year"),
                "subjects": subjects,
            },
        )
