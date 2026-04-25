"""set parent_child_chunking default to true

Revision ID: 20260425_40
Revises: 20260321_39
Create Date: 2026-04-25
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260425_40"
down_revision: str | None = "20260321_39"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "projects",
        "parent_child_chunking",
        server_default="true",
    )


def downgrade() -> None:
    op.alter_column(
        "projects",
        "parent_child_chunking",
        server_default="false",
    )
