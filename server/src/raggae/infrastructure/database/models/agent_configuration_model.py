from uuid import UUID

from sqlalchemy import Boolean, Float, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from raggae.infrastructure.database.models.base import Base


class AgentConfigurationModel(Base):
    __tablename__ = "agent_configurations"
    __table_args__ = (
        UniqueConstraint("owner_id", "owner_type", name="uq_agent_configurations_owner"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    owner_type: Mapped[str] = mapped_column(String(8), nullable=False)
    # Models
    embedding_backend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    embedding_api_key_credential_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    llm_backend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    llm_api_key_credential_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    # Indexing
    chunking_strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    parent_child_chunking: Mapped[bool | None] = mapped_column(Boolean(), nullable=True)
    # Retrieval
    retrieval_strategy: Mapped[str | None] = mapped_column(String(16), nullable=True)
    retrieval_top_k: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    retrieval_min_score: Mapped[float | None] = mapped_column(Float(), nullable=True)
    # Reranking
    reranking_enabled: Mapped[bool | None] = mapped_column(Boolean(), nullable=True)
    reranker_backend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    reranker_model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reranker_candidate_multiplier: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    # Chat history
    chat_history_window_size: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    chat_history_max_chars: Mapped[int | None] = mapped_column(Integer(), nullable=True)
