"""add project retrieval top k

Revision ID: 20260224_26
Revises: 20260224_25
Create Date: 2026-02-24
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260224_26"
down_revision: str | None = "20260224_25"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("retrieval_top_k", sa.Integer(), nullable=False, server_default="8"),
    )
    op.execute(
        "ALTER TABLE projects ADD CONSTRAINT ck_projects_retrieval_top_k "
        "CHECK (retrieval_top_k >= 1 AND retrieval_top_k <= 40)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE projects DROP CONSTRAINT IF EXISTS ck_projects_retrieval_top_k")
    op.drop_column("projects", "retrieval_top_k")
