"""add org credential ids to projects

Revision ID: 20260301_36
Revises: 20260301_35
Create Date: 2026-03-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260301_36"
down_revision: str | None = "20260301_35"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "org_embedding_api_key_credential_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "org_llm_api_key_credential_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_projects_org_embedding_credential",
        "projects",
        "org_model_provider_credentials",
        ["org_embedding_api_key_credential_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_projects_org_llm_credential",
        "projects",
        "org_model_provider_credentials",
        ["org_llm_api_key_credential_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_projects_org_llm_credential", "projects", type_="foreignkey")
    op.drop_constraint("fk_projects_org_embedding_credential", "projects", type_="foreignkey")
    op.drop_column("projects", "org_llm_api_key_credential_id")
    op.drop_column("projects", "org_embedding_api_key_credential_id")
