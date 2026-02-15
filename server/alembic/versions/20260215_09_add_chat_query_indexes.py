"""add chat query indexes

Revision ID: 20260215_09
Revises: 20260215_08
Create Date: 2026-02-15
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260215_09"
down_revision: str | None = "20260215_08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_messages_conversation_created_at "
        "ON messages (conversation_id, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_conversations_project_user_created_at_desc "
        "ON conversations (project_id, user_id, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_conversations_project_user_created_at_desc")
    op.execute("DROP INDEX IF EXISTS ix_messages_conversation_created_at")
