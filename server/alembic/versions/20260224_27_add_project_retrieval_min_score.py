"""add project retrieval min score

Revision ID: 20260224_27
Revises: 20260224_26
Create Date: 2026-02-24 23:10:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260224_27"
down_revision: str | Sequence[str] | None = "20260224_26"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("retrieval_min_score", sa.Float(), nullable=False, server_default="0.3"),
    )
    op.execute(
        "ALTER TABLE projects ADD CONSTRAINT ck_projects_retrieval_min_score "
        "CHECK (retrieval_min_score >= 0.0 AND retrieval_min_score <= 1.0)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE projects DROP CONSTRAINT IF EXISTS ck_projects_retrieval_min_score")
    op.drop_column("projects", "retrieval_min_score")
