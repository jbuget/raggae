"""add organization_default_configs table

Revision ID: 20260322_40
Revises: 20260321_39
Create Date: 2026-03-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260322_40"
down_revision: str | None = "20260321_39"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization_default_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("embedding_backend", sa.String(32), nullable=True),
        sa.Column("llm_backend", sa.String(32), nullable=True),
        sa.Column("chunking_strategy", sa.String(32), nullable=True),
        sa.Column("retrieval_strategy", sa.String(16), nullable=True),
        sa.Column("retrieval_top_k", sa.Integer(), nullable=True),
        sa.Column("retrieval_min_score", sa.Float(), nullable=True),
        sa.Column("reranking_enabled", sa.Boolean(), nullable=True),
        sa.Column("reranker_backend", sa.String(32), nullable=True),
        sa.Column(
            "org_embedding_api_key_credential_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("org_model_provider_credentials.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "org_llm_api_key_credential_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("org_model_provider_credentials.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_organization_default_configs_organization_id",
        "organization_default_configs",
        ["organization_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organization_default_configs_organization_id",
        table_name="organization_default_configs",
    )
    op.drop_table("organization_default_configs")
