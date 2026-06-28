from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from raggae.infrastructure.database.models.base import Base


class ProjectMcpActivationModel(Base):
    __tablename__ = "project_mcp_activations"

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    org_mcp_server_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("org_mcp_servers.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    activated_by_user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
