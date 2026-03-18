"""add locale to users

Revision ID: 20260318_37
Revises: 20260301_36
Create Date: 2026-03-18
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260318_37"
down_revision: str | None = "20260301_36"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("locale", sa.String(2), nullable=False, server_default="en"),
    )


def downgrade() -> None:
    op.drop_column("users", "locale")
