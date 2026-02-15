"""add foreign key from documents to projects

Revision ID: 20260215_05
Revises: 20260215_04
Create Date: 2026-02-15
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260215_05"
down_revision: str | None = "20260215_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_documents_project_id_projects",
        "documents",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_documents_project_id_projects", "documents", type_="foreignkey")
