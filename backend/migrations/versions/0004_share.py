"""searches: share_token + response_json snapshot (public sharing)

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-05
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("searches", sa.Column("share_token", sa.String(22), nullable=True))
    op.add_column("searches", sa.Column("response_json", postgresql.JSONB, nullable=True))
    op.create_index(
        "ix_searches_share_token", "searches", ["share_token"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_searches_share_token", table_name="searches")
    op.drop_column("searches", "response_json")
    op.drop_column("searches", "share_token")
