"""add last_indexed_at to documents

Revision ID: 20260217_20
Revises: 20260217_19
Create Date: 2026-02-17
"""

import sqlalchemy as sa
from alembic import op

revision = "20260217_20"
down_revision = "20260217_19"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("last_indexed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "last_indexed_at")
