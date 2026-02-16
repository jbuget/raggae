"""change embedding dimension from 1536 to 768

Revision ID: 20260216_14
Revises: 20260215_13
Create Date: 2026-02-16
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260216_14"
down_revision: str | None = "20260215_13"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")
    op.execute("DELETE FROM document_chunks")
    op.execute(
        "ALTER TABLE document_chunks "
        "ALTER COLUMN embedding TYPE vector(768) "
        "USING embedding::vector(768)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")
    op.execute("DELETE FROM document_chunks")
    op.execute(
        "ALTER TABLE document_chunks "
        "ALTER COLUMN embedding TYPE vector(1536) "
        "USING embedding::vector(1536)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )
