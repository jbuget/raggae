"""merge user_project_defaults and organization_project_defaults into project_defaults

Revision ID: 20260505_44
Revises: 20260430_43
Create Date: 2026-05-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260505_44"
down_revision: str | None = "20260430_43"
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

    op.execute("""
        INSERT INTO project_defaults (
            id, owner_id, owner_type,
            embedding_backend, embedding_model, embedding_api_key_credential_id,
            llm_backend, llm_model, llm_api_key_credential_id,
            chunking_strategy, parent_child_chunking,
            retrieval_strategy, retrieval_top_k, retrieval_min_score,
            reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier,
            chat_history_window_size, chat_history_max_chars
        )
        SELECT
            gen_random_uuid(), user_id, 'USER',
            embedding_backend, embedding_model, embedding_api_key_credential_id,
            llm_backend, llm_model, llm_api_key_credential_id,
            chunking_strategy, parent_child_chunking,
            retrieval_strategy, retrieval_top_k, retrieval_min_score,
            reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier,
            chat_history_window_size, chat_history_max_chars
        FROM user_project_defaults
    """)

    op.execute("""
        INSERT INTO project_defaults (
            id, owner_id, owner_type,
            embedding_backend, embedding_model, embedding_api_key_credential_id,
            llm_backend, llm_model, llm_api_key_credential_id,
            chunking_strategy, parent_child_chunking,
            retrieval_strategy, retrieval_top_k, retrieval_min_score,
            reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier,
            chat_history_window_size, chat_history_max_chars
        )
        SELECT
            gen_random_uuid(), organization_id, 'ORGA',
            embedding_backend, embedding_model, embedding_api_key_credential_id,
            llm_backend, llm_model, llm_api_key_credential_id,
            chunking_strategy, parent_child_chunking,
            retrieval_strategy, retrieval_top_k, retrieval_min_score,
            reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier,
            chat_history_window_size, chat_history_max_chars
        FROM organization_project_defaults
    """)

    op.drop_table("user_project_defaults")
    op.drop_table("organization_project_defaults")


def downgrade() -> None:
    op.create_table(
        "user_project_defaults",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "organization_project_defaults",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.PrimaryKeyConstraint("organization_id"),
    )

    op.execute("""
        INSERT INTO user_project_defaults (
            user_id,
            embedding_backend, embedding_model, embedding_api_key_credential_id,
            llm_backend, llm_model, llm_api_key_credential_id,
            chunking_strategy, parent_child_chunking,
            retrieval_strategy, retrieval_top_k, retrieval_min_score,
            reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier,
            chat_history_window_size, chat_history_max_chars
        )
        SELECT
            owner_id,
            embedding_backend, embedding_model, embedding_api_key_credential_id,
            llm_backend, llm_model, llm_api_key_credential_id,
            chunking_strategy, parent_child_chunking,
            retrieval_strategy, retrieval_top_k, retrieval_min_score,
            reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier,
            chat_history_window_size, chat_history_max_chars
        FROM project_defaults WHERE owner_type = 'USER'
    """)

    op.execute("""
        INSERT INTO organization_project_defaults (
            organization_id,
            embedding_backend, embedding_model, embedding_api_key_credential_id,
            llm_backend, llm_model, llm_api_key_credential_id,
            chunking_strategy, parent_child_chunking,
            retrieval_strategy, retrieval_top_k, retrieval_min_score,
            reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier,
            chat_history_window_size, chat_history_max_chars
        )
        SELECT
            owner_id,
            embedding_backend, embedding_model, embedding_api_key_credential_id,
            llm_backend, llm_model, llm_api_key_credential_id,
            chunking_strategy, parent_child_chunking,
            retrieval_strategy, retrieval_top_k, retrieval_min_score,
            reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier,
            chat_history_window_size, chat_history_max_chars
        FROM project_defaults WHERE owner_type = 'ORGA'
    """)

    op.drop_table("project_defaults")
