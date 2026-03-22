"""add project_snapshots table

Revision ID: 20260321_39
Revises: 20260319_38
Create Date: 2026-03-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260321_39"
down_revision: str | None = "20260319_38"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("system_prompt", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "chunking_strategy",
            sa.String(32),
            nullable=False,
            server_default="auto",
        ),
        sa.Column(
            "parent_child_chunking",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("embedding_backend", sa.String(32), nullable=True),
        sa.Column("embedding_model", sa.String(128), nullable=True),
        sa.Column(
            "embedding_api_key_credential_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "org_embedding_api_key_credential_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("llm_backend", sa.String(32), nullable=True),
        sa.Column("llm_model", sa.String(128), nullable=True),
        sa.Column(
            "llm_api_key_credential_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "org_llm_api_key_credential_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "retrieval_strategy",
            sa.String(16),
            nullable=False,
            server_default="hybrid",
        ),
        sa.Column("retrieval_top_k", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("retrieval_min_score", sa.Float(), nullable=False, server_default="0.3"),
        sa.Column("chat_history_window_size", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("chat_history_max_chars", sa.Integer(), nullable=False, server_default="4000"),
        sa.Column(
            "reranking_enabled",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("reranker_backend", sa.String(32), nullable=True),
        sa.Column("reranker_model", sa.String(255), nullable=True),
        sa.Column(
            "reranker_candidate_multiplier",
            sa.Integer(),
            nullable=False,
            server_default="3",
        ),
        sa.Column("restored_from_version", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_project_snapshots_project_id_version",
        "project_snapshots",
        ["project_id", "version_number"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_project_snapshots_project_id_version", table_name="project_snapshots")
    op.drop_table("project_snapshots")
