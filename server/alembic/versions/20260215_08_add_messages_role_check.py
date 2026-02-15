"""add role check constraint on messages

Revision ID: 20260215_08
Revises: 20260215_07
Create Date: 2026-02-15
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260215_08"
down_revision: str | None = "20260215_07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_messages_role",
        "messages",
        "role IN ('user', 'assistant', 'system')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_messages_role", "messages", type_="check")
