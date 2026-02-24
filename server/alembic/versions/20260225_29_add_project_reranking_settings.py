"""add project reranking settings

Revision ID: 20260225_29
Revises: 20260224_28
Create Date: 2026-02-25 00:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260225_29"
down_revision: str | Sequence[str] | None = "20260224_28"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("reranking_enabled", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column("projects", sa.Column("reranker_backend", sa.String(length=32), nullable=True))
    op.add_column("projects", sa.Column("reranker_model", sa.String(length=255), nullable=True))
    op.add_column(
        "projects",
        sa.Column("reranker_candidate_multiplier", sa.Integer(), nullable=False, server_default="3"),
    )
    op.execute(
        "ALTER TABLE projects ADD CONSTRAINT ck_projects_reranker_candidate_multiplier "
        "CHECK (reranker_candidate_multiplier >= 1 AND reranker_candidate_multiplier <= 10)"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE projects DROP CONSTRAINT IF EXISTS ck_projects_reranker_candidate_multiplier"
    )
    op.drop_column("projects", "reranker_candidate_multiplier")
    op.drop_column("projects", "reranker_model")
    op.drop_column("projects", "reranker_backend")
    op.drop_column("projects", "reranking_enabled")
