"""refactor project_defaults → agent_configurations avec types PROJECT et APP

Revision ID: 20260506_45
Revises: 20260505_44
Create Date: 2026-05-06

⚠️  IRRÉVERSIBILITÉ PARTIELLE — lire avant d'appliquer en production
-----------------------------------------------------------------------
Le upgrade() déplace les données de config depuis projects vers
agent_configurations puis supprime les colonnes de projects. Le downgrade()
restaure les données via un UPDATE depuis agent_configurations avant de les
supprimer, mais les colonnes *_encrypted (clés API chiffrées) ne peuvent pas
être restaurées — elles sont perdues définitivement au upgrade.

Prérequis avant migration en production :
  1. Effectuer un pg_dump complet de la base de données.
  2. Pour une table projects volumineuse, prévoir une fenêtre de maintenance :
     l'INSERT … SELECT gen_random_uuid() peut poser des verrous sur la table.
"""

import os
import uuid
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260506_45"
down_revision: str | None = "20260505_44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SYSTEM_OWNER_ID = "00000000-0000-0000-0000-000000000001"

CONFIG_COLS = [
    "embedding_backend",
    "embedding_model",
    "embedding_api_key_credential_id",
    "llm_backend",
    "llm_model",
    "llm_api_key_credential_id",
    "chunking_strategy",
    "parent_child_chunking",
    "retrieval_strategy",
    "retrieval_top_k",
    "retrieval_min_score",
    "reranking_enabled",
    "reranker_backend",
    "reranker_model",
    "reranker_candidate_multiplier",
    "chat_history_window_size",
    "chat_history_max_chars",
]

OVERRIDE_COLS = [
    "overrides_models_from_org",
    "overrides_indexing_from_org",
    "overrides_retrieval_from_org",
    "overrides_reranking_from_org",
    "overrides_chat_history_from_org",
    "overrides_models_from_user",
    "overrides_indexing_from_user",
    "overrides_retrieval_from_user",
    "overrides_reranking_from_user",
    "overrides_chat_history_from_user",
]


def upgrade() -> None:
    # 1. Rename table + constraint
    op.rename_table("project_defaults", "agent_configurations")
    op.execute(
        "ALTER TABLE agent_configurations "
        "RENAME CONSTRAINT uq_project_defaults_owner TO uq_agent_configurations_owner"
    )

    # 2. Increase owner_type length to accommodate PROJECT (7 chars) and APP (3 chars)
    op.alter_column(
        "agent_configurations",
        "owner_type",
        type_=sa.String(length=8),
        existing_type=sa.String(length=8),
        nullable=False,
    )

    # 3. Data migration: insert APP row seeded from env vars
    _insert_app_row()

    # 4. Data migration: insert one PROJECT row per project (copy config cols)
    cols = ", ".join(CONFIG_COLS)
    op.execute(
        f"""
        INSERT INTO agent_configurations (
            id, owner_id, owner_type, {cols}
        )
        SELECT
            gen_random_uuid(), id, 'PROJECT', {cols}
        FROM projects
        """
    )

    # 5. Drop config + org credential + override columns from projects
    for col in CONFIG_COLS:
        op.drop_column("projects", col)
    op.drop_column("projects", "embedding_api_key_encrypted")
    op.drop_column("projects", "llm_api_key_encrypted")

    # Remove FK constraints before dropping org credential columns
    op.drop_constraint("fk_projects_org_embedding_credential", "projects", type_="foreignkey")
    op.drop_constraint("fk_projects_org_llm_credential", "projects", type_="foreignkey")
    op.drop_column("projects", "org_embedding_api_key_credential_id")
    op.drop_column("projects", "org_llm_api_key_credential_id")

    for col in OVERRIDE_COLS:
        op.drop_column("projects", col)


def _add_col(col: str) -> None:
    """Helper idempotent pour restaurer une colonne projets dans le downgrade."""
    op.execute(sa.text(f"ALTER TABLE projects ADD COLUMN IF NOT EXISTS {col}"))


def downgrade() -> None:
    # 1. Restore override flag columns (idempotent si downgrade partiel)
    for col in reversed(OVERRIDE_COLS):
        _add_col(f"{col} BOOLEAN NOT NULL DEFAULT false")

    # 2. Restore org credential columns
    cred_ref = "org_model_provider_credentials(id) ON DELETE SET NULL"
    _add_col(f"org_llm_api_key_credential_id UUID REFERENCES {cred_ref}")
    _add_col(f"org_embedding_api_key_credential_id UUID REFERENCES {cred_ref}")

    # 3. Restore encrypted key columns (contenu non restaurable — voir docstring)
    _add_col("llm_api_key_encrypted TEXT")
    _add_col("embedding_api_key_encrypted TEXT")

    # 4. Restore config columns
    nullable_config = [
        ("embedding_backend", "VARCHAR(32)"),
        ("embedding_model", "VARCHAR(128)"),
        ("embedding_api_key_credential_id", "UUID"),
        ("llm_backend", "VARCHAR(32)"),
        ("llm_model", "VARCHAR(128)"),
        ("llm_api_key_credential_id", "UUID"),
        ("reranker_backend", "VARCHAR(32)"),
        ("reranker_model", "VARCHAR(255)"),
    ]
    for col_name, col_type in nullable_config:
        _add_col(f"{col_name} {col_type}")

    nonnull_config = [
        ("chunking_strategy", "VARCHAR(32)", "'auto'"),
        ("parent_child_chunking", "BOOLEAN", "true"),
        ("retrieval_strategy", "VARCHAR(16)", "'hybrid'"),
        ("retrieval_top_k", "INTEGER", "8"),
        ("retrieval_min_score", "FLOAT", "0.3"),
        ("reranking_enabled", "BOOLEAN", "false"),
        ("reranker_candidate_multiplier", "INTEGER", "3"),
        ("chat_history_window_size", "INTEGER", "8"),
        ("chat_history_max_chars", "INTEGER", "4000"),
    ]
    for col_name, col_type, default in nonnull_config:
        _add_col(f"{col_name} {col_type} NOT NULL DEFAULT {default}")

    # 5. Copy config data back from PROJECT rows in agent_configurations
    cols_assignment = ", ".join(f"{c} = ac.{c}" for c in CONFIG_COLS)
    op.execute(
        f"""
        UPDATE projects p
        SET {cols_assignment}
        FROM agent_configurations ac
        WHERE ac.owner_id = p.id AND ac.owner_type = 'PROJECT'
        """
    )

    # 6. Delete PROJECT and APP rows
    op.execute("DELETE FROM agent_configurations WHERE owner_type IN ('PROJECT', 'APP')")

    # 7. Rename constraint + table back
    op.execute(
        "ALTER TABLE agent_configurations "
        "RENAME CONSTRAINT uq_agent_configurations_owner TO uq_project_defaults_owner"
    )
    op.rename_table("agent_configurations", "project_defaults")


def _insert_app_row() -> None:
    def env(key: str, default: str | None = None) -> str | None:
        v = os.environ.get(key, default)
        return v if v else None

    row_id = str(uuid.uuid4())
    llm_backend = env("DEFAULT_LLM_PROVIDER").lower() if env("DEFAULT_LLM_PROVIDER") else None
    llm_model = env("DEFAULT_LLM_MODEL")
    embedding_backend = (
        env("DEFAULT_EMBEDDING_PROVIDER").lower() if env("DEFAULT_EMBEDDING_PROVIDER") else None
    )
    embedding_model = env("DEFAULT_EMBEDDING_MODEL")
    retrieval_strategy = env("RETRIEVAL_DEFAULT_STRATEGY", "hybrid")
    retrieval_top_k_raw = env("RETRIEVAL_DEFAULT_CHUNK_LIMIT", "8")
    retrieval_top_k = int(retrieval_top_k_raw) if retrieval_top_k_raw else None
    retrieval_min_score_raw = env("RETRIEVAL_MIN_SCORE", "0.3")
    retrieval_min_score = float(retrieval_min_score_raw) if retrieval_min_score_raw else None
    reranker_backend = env("RERANKER_BACKEND")
    reranker_model = env("RERANKER_MODEL")
    reranker_mult_raw = env("RERANKER_CANDIDATE_MULTIPLIER", "3")
    reranker_mult = int(reranker_mult_raw) if reranker_mult_raw else None
    chat_window_raw = env("CHAT_HISTORY_WINDOW_SIZE", "8")
    chat_window = int(chat_window_raw) if chat_window_raw else None
    chat_chars_raw = env("CHAT_HISTORY_MAX_CHARS", "4000")
    chat_chars = int(chat_chars_raw) if chat_chars_raw else None

    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO agent_configurations (
                id, owner_id, owner_type,
                embedding_backend, embedding_model,
                llm_backend, llm_model,
                retrieval_strategy, retrieval_top_k, retrieval_min_score,
                reranker_backend, reranker_model, reranker_candidate_multiplier,
                chat_history_window_size, chat_history_max_chars
            ) VALUES (
                :id, :owner_id, 'APP',
                :embedding_backend, :embedding_model,
                :llm_backend, :llm_model,
                :retrieval_strategy, :retrieval_top_k, :retrieval_min_score,
                :reranker_backend, :reranker_model, :reranker_candidate_multiplier,
                :chat_history_window_size, :chat_history_max_chars
            )
            """
        ),
        {
            "id": row_id,
            "owner_id": SYSTEM_OWNER_ID,
            "embedding_backend": embedding_backend,
            "embedding_model": embedding_model,
            "llm_backend": llm_backend,
            "llm_model": llm_model,
            "retrieval_strategy": retrieval_strategy,
            "retrieval_top_k": retrieval_top_k,
            "retrieval_min_score": retrieval_min_score,
            "reranker_backend": reranker_backend,
            "reranker_model": reranker_model,
            "reranker_candidate_multiplier": reranker_mult,
            "chat_history_window_size": chat_window,
            "chat_history_max_chars": chat_chars,
        },
    )
