from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from raggae.infrastructure.database.models.base import Base


class OrganizationDefaultConfigModel(Base):
    __tablename__ = "organization_default_configs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    embedding_backend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    llm_backend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    chunking_strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    retrieval_strategy: Mapped[str | None] = mapped_column(String(16), nullable=True)
    retrieval_top_k: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    retrieval_min_score: Mapped[float | None] = mapped_column(Float(), nullable=True)
    reranking_enabled: Mapped[bool | None] = mapped_column(nullable=True)
    reranker_backend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    org_embedding_api_key_credential_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("org_model_provider_credentials.id", ondelete="SET NULL"),
        nullable=True,
    )
    org_llm_api_key_credential_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("org_model_provider_credentials.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
