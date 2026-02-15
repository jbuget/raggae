"""add document processing strategy column

Revision ID: 20260215_03
Revises: 20260215_02
Create Date: 2026-02-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260215_03"
down_revision: str | None = "20260215_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("processing_strategy", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "processing_strategy")
