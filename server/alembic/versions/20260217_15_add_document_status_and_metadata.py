"""add document status and metadata columns

Revision ID: 20260217_15
Revises: 20260216_14
Create Date: 2026-02-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260217_15"
down_revision: str | None = "20260216_14"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("status", sa.String(16), nullable=False, server_default="indexed"),
    )
    op.add_column(
        "documents",
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("language", sa.String(8), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("keywords", JSONB(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("authors", JSONB(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("document_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("title", sa.String(512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "title")
    op.drop_column("documents", "document_date")
    op.drop_column("documents", "authors")
    op.drop_column("documents", "keywords")
    op.drop_column("documents", "language")
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "status")
