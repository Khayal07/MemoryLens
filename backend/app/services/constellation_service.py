"""Constellation: every item the user has found (search history) or saved
(collections) as nodes, linked by pgvector cosine similarity. Free-form gpt:* rows
have no embedding, so they float unlinked — included on purpose: they're real finds,
just not verifiable against catalog vectors."""

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.infra.models import (
    Category,
    Collection,
    CollectionItem,
    Item,
    Search,
    SearchResult,
)
from app.schemas.constellation import (
    ConstellationEdge,
    ConstellationNode,
    ConstellationResponse,
)

# Node cap keeps the pairwise similarity query and the frontend layout cheap.
_MAX_NODES = 60
# Keep at most this many strongest edges per node…
_EDGES_PER_NODE = 3
# …and only when the cosine similarity is at least this (bge "related" territory).
_MIN_SIMILARITY = 0.55


def build(db: Session, user_id: int) -> ConstellationResponse:
    nodes = _collect_nodes(db, user_id)
    if not nodes:
        return ConstellationResponse()
    edges = _similarity_edges(db, [n.id for n in nodes])
    return ConstellationResponse(nodes=nodes, edges=edges)


def _collect_nodes(db: Session, user_id: int) -> list[ConstellationNode]:
    # Items surfaced by the user's searches, most-seen first.
    searched = db.execute(
        select(Item, Category.key, func.count(SearchResult.id).label("seen"))
        .join(SearchResult, SearchResult.item_id == Item.id)
        .join(Search, Search.id == SearchResult.search_id)
        .join(Category, Category.id == Item.category_id)
        .where(Search.user_id == user_id)
        .group_by(Item.id, Category.key)
        .order_by(func.count(SearchResult.id).desc(), Item.id.desc())
        .limit(_MAX_NODES)
    ).all()

    # Items saved to any of the user's collections.
    saved = db.execute(
        select(Item, Category.key)
        .join(CollectionItem, CollectionItem.item_id == Item.id)
        .join(Collection, Collection.id == CollectionItem.collection_id)
        .join(Category, Category.id == Item.category_id)
        .where(Collection.user_id == user_id)
        .limit(_MAX_NODES)
    ).all()

    by_id: dict[int, ConstellationNode] = {}
    for item, cat_key, seen in searched:
        by_id[item.id] = ConstellationNode(
            id=item.id,
            title=item.title,
            category=cat_key,
            image_url=item.image_url,
            source_url=item.source_url,
            seen_count=int(seen),
        )
    for item, cat_key in saved:
        if item.id not in by_id:
            by_id[item.id] = ConstellationNode(
                id=item.id,
                title=item.title,
                category=cat_key,
                image_url=item.image_url,
                source_url=item.source_url,
                seen_count=1,
            )
    return list(by_id.values())[:_MAX_NODES]


def _similarity_edges(db: Session, item_ids: list[int]) -> list[ConstellationEdge]:
    """Pairwise cosine similarity between the nodes' embeddings (one SQL pass over
    ≤ C(60,2) pairs), then trim to the strongest few per node. Ids without an
    embedding (gpt:* rows) simply never appear."""
    if len(item_ids) < 2:
        return []
    rows = db.execute(
        text(
            """
            SELECT a.item_id AS a, b.item_id AS b,
                   1 - (a.embedding <=> b.embedding) AS sim
            FROM item_embeddings a
            JOIN item_embeddings b ON a.item_id < b.item_id
            WHERE a.item_id = ANY(:ids) AND b.item_id = ANY(:ids)
              AND 1 - (a.embedding <=> b.embedding) >= :min_sim
            ORDER BY sim DESC
            """
        ),
        {"ids": item_ids, "min_sim": _MIN_SIMILARITY},
    ).all()

    per_node: dict[int, int] = {}
    edges: list[ConstellationEdge] = []
    for a, b, sim in rows:  # strongest first
        if per_node.get(a, 0) >= _EDGES_PER_NODE or per_node.get(b, 0) >= _EDGES_PER_NODE:
            continue
        edges.append(ConstellationEdge(a=a, b=b, weight=round(min(1.0, max(0.0, sim)), 3)))
        per_node[a] = per_node.get(a, 0) + 1
        per_node[b] = per_node.get(b, 0) + 1
    return edges
