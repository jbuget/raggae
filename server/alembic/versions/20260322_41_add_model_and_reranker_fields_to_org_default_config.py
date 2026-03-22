"""add model and reranker fields to organization_default_configs

Revision ID: 20260322_41
Revises: 20260322_40
Create Date: 2026-03-22
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260322_41"
down_revision: str | None = "20260322_40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "organization_default_configs",
        sa.Column("embedding_model", sa.String(128), nullable=True),
    )
    op.add_column(
        "organization_default_configs",
        sa.Column("llm_model", sa.String(128), nullable=True),
    )
    op.add_column(
        "organization_default_configs",
        sa.Column("parent_child_chunking", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "organization_default_configs",
        sa.Column("reranker_model", sa.String(255), nullable=True),
    )
    op.add_column(
        "organization_default_configs",
        sa.Column("reranker_candidate_multiplier", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organization_default_configs", "reranker_candidate_multiplier")
    op.drop_column("organization_default_configs", "reranker_model")
    op.drop_column("organization_default_configs", "parent_child_chunking")
    op.drop_column("organization_default_configs", "llm_model")
    op.drop_column("organization_default_configs", "embedding_model")
