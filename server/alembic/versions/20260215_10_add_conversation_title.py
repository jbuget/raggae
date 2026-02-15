"""add title column to conversations

Revision ID: 20260215_10
Revises: 20260215_09
Create Date: 2026-02-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260215_10"
down_revision: str | None = "20260215_09"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("title", sa.String(length=255), nullable=True))
    op.execute("UPDATE conversations SET title = 'New conversation' WHERE title IS NULL")


def downgrade() -> None:
    op.drop_column("conversations", "title")
