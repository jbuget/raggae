"""drop unique active credential constraint

Revision ID: 20260224_24
Revises: 20260217_23
Create Date: 2026-02-24
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260224_24"
down_revision: str | None = "20260217_23"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(
        "uq_user_provider_active_credential",
        table_name="user_model_provider_credentials",
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    op.create_index(
        "uq_user_provider_active_credential",
        "user_model_provider_credentials",
        ["user_id", "provider"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )
