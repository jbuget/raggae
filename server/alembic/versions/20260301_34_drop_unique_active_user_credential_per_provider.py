"""drop unique active user credential per provider

Revision ID: 20260301_34
Revises: 20260226_33
Create Date: 2026-03-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260301_34"
down_revision: str | None = "20260226_33"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Index already dropped in migration 20260224_24 — no-op
    pass


def downgrade() -> None:
    op.create_index(
        "uq_user_provider_active_credential",
        "user_model_provider_credentials",
        ["user_id", "provider"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )
