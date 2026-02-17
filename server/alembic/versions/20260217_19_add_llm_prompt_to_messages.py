"""add llm_prompt to messages

Revision ID: 20260217_19
Revises: 20260217_18
Create Date: 2026-02-17
"""

from alembic import op
import sqlalchemy as sa

revision = "20260217_19"
down_revision = "20260217_18"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("llm_prompt", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "llm_prompt")
