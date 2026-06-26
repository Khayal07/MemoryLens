"""initial schema: users, categories, items, embeddings, searches

Revision ID: 0001
Revises:
Create Date: 2026-06-26
"""
from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

from alembic import op
from app.domain.categories import CATEGORIES
from app.infra.models import EMBEDDING_DIM

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("key", sa.String(32), nullable=False),
        sa.Column("display_name", sa.String(64), nullable=False),
        sa.Column("config_json", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.UniqueConstraint("key", name="uq_categories_key"),
    )
    op.create_index("ix_categories_key", "categories", ["key"])

    op.create_table(
        "items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("external_id", sa.String(128), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("image_url", sa.Text),
        sa.Column("source_url", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("category_id", "external_id", name="uq_item_external"),
    )
    op.create_index("ix_items_category_id", "items", ["category_id"])
    op.create_index("ix_items_title", "items", ["title"])

    op.create_table(
        "item_embeddings",
        sa.Column(
            "item_id",
            sa.Integer,
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column("search_tsv", postgresql.TSVECTOR),
    )
    # HNSW for vector kNN (cosine); GIN for keyword/tsvector search.
    op.execute(
        "CREATE INDEX ix_item_embeddings_vec ON item_embeddings "
        "USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute(
        "CREATE INDEX ix_item_embeddings_tsv ON item_embeddings USING gin (search_tsv)"
    )

    op.create_table(
        "searches",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("raw_query", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_searches_user_id", "searches", ["user_id"])
    op.create_index("ix_searches_category_id", "searches", ["category_id"])

    op.create_table(
        "search_results",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "search_id",
            sa.Integer,
            sa.ForeignKey("searches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("items.id"), nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("rank", sa.Integer, nullable=False),
        sa.Column("reason", sa.Text),
    )
    op.create_index("ix_search_results_search_id", "search_results", ["search_id"])

    # Seed the canonical V1 categories.
    categories_tbl = sa.table(
        "categories",
        sa.column("key", sa.String),
        sa.column("display_name", sa.String),
        sa.column("config_json", postgresql.JSONB),
    )
    op.bulk_insert(
        categories_tbl,
        [
            {
                "key": c["key"],
                "display_name": c["display_name"],
                "config_json": c["config"],
            }
            for c in CATEGORIES
        ],
    )


def downgrade() -> None:
    op.drop_table("search_results")
    op.drop_table("searches")
    op.drop_table("item_embeddings")
    op.drop_table("items")
    op.drop_table("categories")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
