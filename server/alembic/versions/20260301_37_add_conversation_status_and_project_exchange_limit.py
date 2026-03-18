"""add conversation status and project exchange limit

Revision ID: 20260301_37
Revises: 20260301_36
Create Date: 2026-03-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260301_37"
down_revision: str | None = "20260301_36"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column(
            "status",
            sa.String(16),
            nullable=False,
            server_default="active",
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "max_exchanges",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "closing_message",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("projects", "closing_message")
    op.drop_column("projects", "max_exchanges")
    op.drop_column("conversations", "status")
