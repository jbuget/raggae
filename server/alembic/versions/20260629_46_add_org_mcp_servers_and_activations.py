"""add org mcp servers and project activations

Revision ID: 20260629_46
Revises: 20260506_45
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260629_46"
down_revision: str | None = "20260506_45"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "org_mcp_servers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("auth_type", sa.String(length=16), nullable=False),
        sa.Column("encrypted_bearer_token", sa.Text(), nullable=True),
        sa.Column("token_fingerprint", sa.String(length=128), nullable=True),
        sa.Column("token_suffix", sa.String(length=16), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "tools_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("tools_snapshot_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "timeout_seconds",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("30"),
        ),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "slug", name="uq_org_mcp_servers_org_slug"),
    )
    op.create_index(
        "ix_org_mcp_servers_organization_id",
        "org_mcp_servers",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "project_mcp_activations",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_mcp_server_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activated_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["org_mcp_server_id"], ["org_mcp_servers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("project_id", "org_mcp_server_id"),
    )
    op.create_index(
        "ix_project_mcp_activations_org_mcp_server_id",
        "project_mcp_activations",
        ["org_mcp_server_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_project_mcp_activations_org_mcp_server_id",
        table_name="project_mcp_activations",
    )
    op.drop_table("project_mcp_activations")
    op.drop_index(
        "ix_org_mcp_servers_organization_id",
        table_name="org_mcp_servers",
    )
    op.drop_table("org_mcp_servers")
