"""add project api key credential ids

Revision ID: 20260217_23
Revises: 20260217_22
Create Date: 2026-02-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260217_23"
down_revision: Union[str, None] = "20260217_22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("embedding_api_key_credential_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("llm_api_key_credential_id", sa.UUID(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("projects", "llm_api_key_credential_id")
    op.drop_column("projects", "embedding_api_key_credential_id")
