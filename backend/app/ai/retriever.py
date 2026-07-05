"""Hybrid retriever: vector kNN (pgvector, semantic) + keyword (tsvector, lexical),
fused with RRF. Both legs are hard-filtered by category, so a Movies search never
touches Song rows. Returns category-grounded candidates — no hallucinated titles."""

from sqlalchemy import Text, cast, func, select
from sqlalchemy.dialects.postgresql import TSQUERY
from sqlalchemy.orm import Session

from app.ai.embedder import get_embedder
from app.ai.fusion import reciprocal_rank_fusion
from app.ai.types import Candidate
from app.core.config import get_settings
from app.infra.models import Item, ItemEmbedding


def find_similar(db: Session, item_id: int, k: int = 6) -> list[Item]:
    """Nearest catalog neighbours of an item by embedding cosine distance, within the
    same category and excluding the item itself. Powers the "more like this" section.
    Returns [] if the item or its embedding is missing (e.g. a free-form answer)."""
    source = db.get(Item, item_id)
    source_emb = db.get(ItemEmbedding, item_id)
    if source is None or source_emb is None:
        return []
    distance = ItemEmbedding.embedding.cosine_distance(source_emb.embedding).label("distance")
    rows = db.execute(
        select(Item)
        .join(ItemEmbedding, ItemEmbedding.item_id == Item.id)
        .where(Item.category_id == source.category_id, Item.id != item_id)
        .order_by(distance)
        .limit(k)
    ).scalars().all()
    return list(rows)


class HybridRetriever:
    def __init__(self, top_vector: int = 50, top_keyword: int = 50) -> None:
        self.embedder = get_embedder()
        self.top_vector = top_vector
        self.top_keyword = top_keyword
        settings = get_settings()
        self.weights = [settings.rrf_vector_weight, settings.rrf_keyword_weight]

    def search(
        self,
        db: Session,
        category_id: int,
        query: str,
        k: int = 30,
        embed_text: str | None = None,
    ) -> list[Candidate]:
        # `embed_text` lets HyDE feed an expanded text to the semantic leg while the
        # keyword leg keeps the user's literal terms.
        query_vec = self.embedder.embed_query(embed_text or query)
        vector_hits = self._vector_search(db, category_id, query_vec)
        keyword_hits = self._keyword_search(db, category_id, query)

        row_map: dict[int, Item] = {item.id: item for item, _ in [*vector_hits, *keyword_hits]}
        fused = reciprocal_rank_fusion(
            [[item.id for item, _ in vector_hits], [item.id for item, _ in keyword_hits]],
            weights=self.weights,
        )

        candidates: list[Candidate] = []
        for item_id, score in fused[:k]:
            item = row_map[item_id]
            candidates.append(
                Candidate(
                    item_id=item.id,
                    title=item.title,
                    description=item.description or "",
                    image_url=item.image_url,
                    source_url=item.source_url,
                    metadata=item.item_metadata,
                    retrieval_score=score,
                )
            )
        return candidates

    def _vector_search(
        self, db: Session, category_id: int, query_vec: list[float]
    ) -> list[tuple[Item, float]]:
        distance = ItemEmbedding.embedding.cosine_distance(query_vec).label("distance")
        rows = db.execute(
            select(Item, distance)
            .join(ItemEmbedding, ItemEmbedding.item_id == Item.id)
            .where(Item.category_id == category_id)
            .order_by(distance)
            .limit(self.top_vector)
        ).all()
        return [(item, 1.0 - dist) for item, dist in rows]

    def _keyword_search(
        self, db: Session, category_id: int, query: str
    ) -> list[tuple[Item, float]]:
        # plainto_tsquery ANDs every term, which a long fuzzy memory almost never
        # satisfies. Reuse its stemming/stopword handling but OR the lexemes so any
        # matching clue surfaces a candidate (ts_rank still rewards more overlap).
        tsquery = cast(
            func.replace(cast(func.plainto_tsquery("english", query), Text), "&", "|"),
            TSQUERY,
        )
        rank = func.ts_rank(ItemEmbedding.search_tsv, tsquery).label("rank")
        rows = db.execute(
            select(Item, rank)
            .join(ItemEmbedding, ItemEmbedding.item_id == Item.id)
            .where(
                Item.category_id == category_id,
                ItemEmbedding.search_tsv.op("@@")(tsquery),
            )
            .order_by(rank.desc())
            .limit(self.top_keyword)
        ).all()
        return [(item, float(r)) for item, r in rows]
