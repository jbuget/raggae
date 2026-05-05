"""add project_defaults table with user and org defaults

Revision ID: 20260505_44
Revises: 20260427_41
Create Date: 2026-05-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260505_44"
down_revision: str | None = "20260427_41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_defaults",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_type", sa.String(length=8), nullable=False),
        sa.Column("embedding_backend", sa.String(length=32), nullable=True),
        sa.Column("embedding_model", sa.String(length=128), nullable=True),
        sa.Column("embedding_api_key_credential_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("llm_backend", sa.String(length=32), nullable=True),
        sa.Column("llm_model", sa.String(length=128), nullable=True),
        sa.Column("llm_api_key_credential_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("chunking_strategy", sa.String(length=32), nullable=True),
        sa.Column("parent_child_chunking", sa.Boolean(), nullable=True),
        sa.Column("retrieval_strategy", sa.String(length=16), nullable=True),
        sa.Column("retrieval_top_k", sa.Integer(), nullable=True),
        sa.Column("retrieval_min_score", sa.Float(), nullable=True),
        sa.Column("reranking_enabled", sa.Boolean(), nullable=True),
        sa.Column("reranker_backend", sa.String(length=32), nullable=True),
        sa.Column("reranker_model", sa.String(length=255), nullable=True),
        sa.Column("reranker_candidate_multiplier", sa.Integer(), nullable=True),
        sa.Column("chat_history_window_size", sa.Integer(), nullable=True),
        sa.Column("chat_history_max_chars", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "owner_type", name="uq_project_defaults_owner"),
    )

    op.add_column(
        "projects",
        sa.Column(
            "overrides_models_from_org",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "overrides_indexing_from_org",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "overrides_retrieval_from_org",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "overrides_reranking_from_org",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "overrides_chat_history_from_org",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "overrides_models_from_user",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "overrides_indexing_from_user",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "overrides_retrieval_from_user",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "overrides_reranking_from_user",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "overrides_chat_history_from_user",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("projects", "overrides_chat_history_from_user")
    op.drop_column("projects", "overrides_reranking_from_user")
    op.drop_column("projects", "overrides_retrieval_from_user")
    op.drop_column("projects", "overrides_indexing_from_user")
    op.drop_column("projects", "overrides_models_from_user")
    op.drop_column("projects", "overrides_chat_history_from_org")
    op.drop_column("projects", "overrides_reranking_from_org")
    op.drop_column("projects", "overrides_retrieval_from_org")
    op.drop_column("projects", "overrides_indexing_from_org")
    op.drop_column("projects", "overrides_models_from_org")
    op.drop_table("project_defaults")
