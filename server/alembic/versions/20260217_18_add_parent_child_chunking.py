"""add parent-child chunking columns

Revision ID: 20260217_18
Revises: 20260217_17
Create Date: 2026-02-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260217_18"
down_revision: str | None = "20260217_17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "document_chunks",
        sa.Column(
            "chunk_level",
            sa.String(16),
            nullable=False,
            server_default="standard",
        ),
    )
    op.add_column(
        "document_chunks",
        sa.Column(
            "parent_chunk_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_chunks.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_document_chunks_parent_chunk_id",
        "document_chunks",
        ["parent_chunk_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_document_chunks_parent_chunk_id", table_name="document_chunks")
    op.drop_column("document_chunks", "parent_chunk_id")
    op.drop_column("document_chunks", "chunk_level")
