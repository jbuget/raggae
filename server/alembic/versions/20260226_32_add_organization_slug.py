"""add organization slug

Revision ID: 20260226_32
Revises: 20260226_31
Create Date: 2026-02-26 01:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260226_32"
down_revision: str | Sequence[str] | None = "20260226_31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("slug", sa.String(length=128), nullable=True))
    op.create_index("uq_organizations_slug", "organizations", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_organizations_slug", table_name="organizations")
    op.drop_column("organizations", "slug")
