"""Live RAWG adapter (games). Needs a free RAWG_API_KEY. The list endpoint has no
plot, so we fetch each game's detail for `description_raw` — memory fragments are
usually about story/characters, not genre tags."""

from collections.abc import Iterable

import httpx

from app.core.config import get_settings
from app.ingest.base import NormalizedItem

LIST_URL = "https://api.rawg.io/api/games"
DETAIL_URL = "https://api.rawg.io/api/games/{id}"


class RAWGAdapter:
    category_key = "games"

    def __init__(self) -> None:
        self._key = get_settings().rawg_api_key

    def fetch(self, limit: int = 300) -> Iterable[NormalizedItem]:
        if not self._key:
            raise RuntimeError("RAWG_API_KEY is not set")
        fetched = 0
        page = 1
        with httpx.Client(timeout=30.0, headers={"User-Agent": "MemoryLens/0.1"}) as client:
            while fetched < limit:
                resp = client.get(
                    LIST_URL,
                    params={
                        "key": self._key,
                        # "-added" ≈ popularity (how many users added it), so we get the
                        # iconic games people actually half-remember, not obscure
                        # high-"rating" indies.
                        "ordering": "-added",
                        "page_size": 40,
                        "page": page,
                    },
                )
                resp.raise_for_status()
                results = resp.json().get("results", [])
                if not results:
                    break
                for game in results:
                    if fetched >= limit:
                        break
                    item = self._normalize(client, game)
                    if item:
                        yield item
                        fetched += 1
                page += 1

    def _normalize(self, client: httpx.Client, game: dict) -> NormalizedItem | None:
        name = game.get("name")
        game_id = game.get("id")
        if not name or not game_id:
            return None
        genres = [g["name"] for g in game.get("genres", [])]

        description = self._fetch_plot(client, game_id)
        if not description:
            description = f"A {', '.join(genres) or 'video'} game."

        return NormalizedItem(
            external_id=f"rawg:{game_id}",
            title=name,
            description=description,
            image_url=game.get("background_image"),
            source_url=f"https://rawg.io/games/{game.get('slug', '')}",
            metadata={"year": (game.get("released") or "")[:4], "genres": genres},
        )

    def _fetch_plot(self, client: httpx.Client, game_id: int) -> str:
        try:
            resp = client.get(DETAIL_URL.format(id=game_id), params={"key": self._key})
            if resp.status_code == 200:
                return (resp.json().get("description_raw") or "")[:600]
        except httpx.HTTPError:
            pass
        return ""
