"""add user model provider credentials

Revision ID: 20260217_21
Revises: 20260217_20
Create Date: 2026-02-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260217_21"
down_revision: str | None = "20260217_20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_model_provider_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("encrypted_api_key", sa.Text(), nullable=False),
        sa.Column("key_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("key_suffix", sa.String(length=16), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_model_provider_credentials_user_id",
        "user_model_provider_credentials",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_model_provider_credentials_provider",
        "user_model_provider_credentials",
        ["provider"],
        unique=False,
    )
    op.create_index(
        "uq_user_provider_active_credential",
        "user_model_provider_credentials",
        ["user_id", "provider"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_user_provider_active_credential",
        table_name="user_model_provider_credentials",
        postgresql_where=sa.text("is_active = true"),
    )
    op.drop_index(
        "ix_user_model_provider_credentials_provider",
        table_name="user_model_provider_credentials",
    )
    op.drop_index(
        "ix_user_model_provider_credentials_user_id",
        table_name="user_model_provider_credentials",
    )
    op.drop_table("user_model_provider_credentials")
