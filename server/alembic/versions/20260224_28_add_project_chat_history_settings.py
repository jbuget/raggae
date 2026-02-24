"""add project chat history settings

Revision ID: 20260224_28
Revises: 20260224_27
Create Date: 2026-02-24 23:40:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260224_28"
down_revision: str | Sequence[str] | None = "20260224_27"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("chat_history_window_size", sa.Integer(), nullable=False, server_default="8"),
    )
    op.add_column(
        "projects",
        sa.Column("chat_history_max_chars", sa.Integer(), nullable=False, server_default="4000"),
    )
    op.execute(
        "ALTER TABLE projects ADD CONSTRAINT ck_projects_chat_history_window_size "
        "CHECK (chat_history_window_size >= 1 AND chat_history_window_size <= 40)"
    )
    op.execute(
        "ALTER TABLE projects ADD CONSTRAINT ck_projects_chat_history_max_chars "
        "CHECK (chat_history_max_chars >= 128 AND chat_history_max_chars <= 16000)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE projects DROP CONSTRAINT IF EXISTS ck_projects_chat_history_max_chars")
    op.execute(
        "ALTER TABLE projects DROP CONSTRAINT IF EXISTS ck_projects_chat_history_window_size"
    )
    op.drop_column("projects", "chat_history_max_chars")
    op.drop_column("projects", "chat_history_window_size")
