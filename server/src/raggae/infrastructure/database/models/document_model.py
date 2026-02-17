from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from raggae.infrastructure.database.models.base import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer(), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    processing_strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="indexed")
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    keywords: Mapped[list[str] | None] = mapped_column(JSONB(), nullable=True)
    authors: Mapped[list[str] | None] = mapped_column(JSONB(), nullable=True)
    document_date: Mapped[date | None] = mapped_column(Date(), nullable=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
