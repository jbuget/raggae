from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from raggae.infrastructure.database.models.base import Base


class OrgMcpServerModel(Base):
    __tablename__ = "org_mcp_servers"
    __table_args__ = (UniqueConstraint("organization_id", "slug", name="uq_org_mcp_servers_org_slug"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(Text(), nullable=False)
    auth_type: Mapped[str] = mapped_column(String(16), nullable=False)
    encrypted_bearer_token: Mapped[str | None] = mapped_column(Text(), nullable=True)
    token_fingerprint: Mapped[str | None] = mapped_column(String(128), nullable=True)
    token_suffix: Mapped[str | None] = mapped_column(String(16), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    tools_snapshot: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    tools_snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer(), nullable=False, default=30)
    created_by_user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
