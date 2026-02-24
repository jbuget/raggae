from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from raggae.infrastructure.database.models.base import Base


class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    system_prompt: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    is_published: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    chunking_strategy: Mapped[str] = mapped_column(
        String(32), nullable=False, default="auto", server_default="auto"
    )
    parent_child_chunking: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, default=False, server_default="false"
    )
    reindex_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="idle", server_default="idle"
    )
    reindex_progress: Mapped[int] = mapped_column(
        Integer(), nullable=False, default=0, server_default="0"
    )
    reindex_total: Mapped[int] = mapped_column(
        Integer(), nullable=False, default=0, server_default="0"
    )
    embedding_backend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    embedding_api_key_encrypted: Mapped[str | None] = mapped_column(Text(), nullable=True)
    embedding_api_key_credential_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    llm_backend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    llm_api_key_encrypted: Mapped[str | None] = mapped_column(Text(), nullable=True)
    llm_api_key_credential_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
