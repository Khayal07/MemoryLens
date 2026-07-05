"""result_feedback (thumbs up/down on grounded results)

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-05
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "result_feedback",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("search_id", sa.Integer, sa.ForeignKey("searches.id", ondelete="SET NULL")),
        sa.Column(
            "item_id",
            sa.Integer,
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("vote", sa.SmallInteger, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "item_id", name="uq_feedback_user_item"),
    )
    op.create_index("ix_result_feedback_user_id", "result_feedback", ["user_id"])
    op.create_index("ix_result_feedback_item_id", "result_feedback", ["item_id"])


def downgrade() -> None:
    op.drop_table("result_feedback")
