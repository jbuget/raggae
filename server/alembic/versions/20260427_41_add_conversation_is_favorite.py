"""add is_favorite to conversations

Revision ID: 20260427_41
Revises: 20260425_40
Create Date: 2026-04-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260427_41"
down_revision: str | None = "20260425_40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_index(
        "ix_conversations_user_favorite",
        "conversations",
        ["user_id", "is_favorite"],
        postgresql_where=sa.text("is_favorite = true"),
    )


def downgrade() -> None:
    op.drop_index("ix_conversations_user_favorite", table_name="conversations")
    op.drop_column("conversations", "is_favorite")
