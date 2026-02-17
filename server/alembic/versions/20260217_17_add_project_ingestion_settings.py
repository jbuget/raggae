"""add project ingestion settings

Revision ID: 20260217_17
Revises: 20260217_16
Create Date: 2026-02-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260217_17"
down_revision: str | None = "20260217_16"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("chunking_strategy", sa.String(length=32), nullable=False, server_default="auto"),
    )
    op.add_column(
        "projects",
        sa.Column(
            "parent_child_chunking",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column("reindex_status", sa.String(length=32), nullable=False, server_default="idle"),
    )
    op.add_column(
        "projects",
        sa.Column(
            "reindex_progress",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "reindex_total",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("projects", "reindex_total")
    op.drop_column("projects", "reindex_progress")
    op.drop_column("projects", "reindex_status")
    op.drop_column("projects", "parent_child_chunking")
    op.drop_column("projects", "chunking_strategy")
