"""add org model provider credentials

Revision ID: 20260301_35
Revises: 20260301_34
Create Date: 2026-03-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260301_35"
down_revision: str | None = "20260301_34"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "org_model_provider_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_org_model_provider_credentials_organization_id",
        "org_model_provider_credentials",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_org_model_provider_credentials_provider",
        "org_model_provider_credentials",
        ["provider"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_org_model_provider_credentials_provider",
        table_name="org_model_provider_credentials",
    )
    op.drop_index(
        "ix_org_model_provider_credentials_organization_id",
        table_name="org_model_provider_credentials",
    )
    op.drop_table("org_model_provider_credentials")
