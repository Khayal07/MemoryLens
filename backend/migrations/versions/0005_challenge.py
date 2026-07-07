"""daily_challenges + challenge_attempts (daily guessing game)

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-08
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "daily_challenges",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("challenge_date", sa.Date, nullable=False),
        sa.Column(
            "item_id",
            sa.Integer,
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("clues", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_daily_challenges_challenge_date",
        "daily_challenges",
        ["challenge_date"],
        unique=True,
    )
    op.create_table(
        "challenge_attempts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "challenge_id",
            sa.Integer,
            sa.ForeignKey("daily_challenges.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("guesses_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("solved", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "challenge_id", name="uq_attempt_user_challenge"),
    )
    op.create_index("ix_challenge_attempts_user_id", "challenge_attempts", ["user_id"])
    op.create_index(
        "ix_challenge_attempts_challenge_id", "challenge_attempts", ["challenge_id"]
    )


def downgrade() -> None:
    op.drop_table("challenge_attempts")
    op.drop_table("daily_challenges")
