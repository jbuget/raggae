"""add entra_id and make hashed_password nullable for SSO support

Revision ID: 20260319_38
Revises: 20260318_37
Create Date: 2026-03-19
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260319_38"
down_revision: str | None = "20260318_37"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("users", "hashed_password", nullable=True)
    op.add_column("users", sa.Column("entra_id", sa.String(255), nullable=True))
    op.create_index(
        "ix_users_entra_id",
        "users",
        ["entra_id"],
        unique=True,
        postgresql_where=sa.text("entra_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_users_entra_id", table_name="users")
    op.drop_column("users", "entra_id")
    op.alter_column("users", "hashed_password", nullable=False)
