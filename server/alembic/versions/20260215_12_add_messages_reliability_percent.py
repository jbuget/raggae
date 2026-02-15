"""add reliability percent to messages

Revision ID: 20260215_12
Revises: 20260215_11
Create Date: 2026-02-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260215_12"
down_revision: str | None = "20260215_11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("reliability_percent", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "reliability_percent")
