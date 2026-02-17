"""add project ai provider settings

Revision ID: 20260217_22
Revises: 20260217_21
Create Date: 2026-02-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260217_22"
down_revision: str | None = "20260217_21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("embedding_backend", sa.String(length=32), nullable=True))
    op.add_column("projects", sa.Column("embedding_model", sa.String(length=128), nullable=True))
    op.add_column("projects", sa.Column("embedding_api_key_encrypted", sa.Text(), nullable=True))
    op.add_column("projects", sa.Column("llm_backend", sa.String(length=32), nullable=True))
    op.add_column("projects", sa.Column("llm_model", sa.String(length=128), nullable=True))
    op.add_column("projects", sa.Column("llm_api_key_encrypted", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("projects", "llm_api_key_encrypted")
    op.drop_column("projects", "llm_model")
    op.drop_column("projects", "llm_backend")
    op.drop_column("projects", "embedding_api_key_encrypted")
    op.drop_column("projects", "embedding_model")
    op.drop_column("projects", "embedding_backend")
