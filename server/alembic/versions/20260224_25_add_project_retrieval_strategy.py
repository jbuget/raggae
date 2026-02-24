"""add project retrieval strategy

Revision ID: 20260224_25
Revises: 20260224_24
Create Date: 2026-02-24
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260224_25"
down_revision: str | None = "20260224_24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "retrieval_strategy",
            sa.String(length=16),
            nullable=False,
            server_default="hybrid",
        ),
    )
    op.execute(
        "ALTER TABLE projects ADD CONSTRAINT ck_projects_retrieval_strategy "
        "CHECK (retrieval_strategy IN ('vector', 'fulltext', 'hybrid'))"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE projects DROP CONSTRAINT IF EXISTS ck_projects_retrieval_strategy")
    op.drop_column("projects", "retrieval_strategy")
