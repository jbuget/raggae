"""restore missing revision 20260225_30 as no-op

Revision ID: 20260225_30
Revises: 20260225_29
Create Date: 2026-02-25 01:05:00.000000
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "20260225_30"
down_revision: str | Sequence[str] | None = "20260225_29"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Intentionally no-op: this revision was removed and is restored
    # to keep alembic_version continuity in existing databases.
    return


def downgrade() -> None:
    return
