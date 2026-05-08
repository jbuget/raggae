from dataclasses import dataclass
from uuid import UUID

from raggae.domain.entities.organization_project_defaults import OrganizationProjectDefaults


@dataclass
class OrgProjectDefaultsDTO:
    """Data Transfer Object for OrganizationProjectDefaults."""

    organization_id: UUID
    # Models
    embedding_backend: str | None
    embedding_model: str | None
    embedding_api_key_credential_id: UUID | None
    llm_backend: str | None
    llm_model: str | None
    llm_api_key_credential_id: UUID | None
    # Indexing
    chunking_strategy: str | None
    parent_child_chunking: bool | None
    # Retrieval
    retrieval_strategy: str | None
    retrieval_top_k: int | None
    retrieval_min_score: float | None
    # Reranking
    reranking_enabled: bool | None
    reranker_backend: str | None
    reranker_model: str | None
    reranker_candidate_multiplier: int | None
    # Chat history
    chat_history_window_size: int | None
    chat_history_max_chars: int | None

    @classmethod
    def from_entity(cls, entity: OrganizationProjectDefaults) -> "OrgProjectDefaultsDTO":
        return cls(
            organization_id=entity.organization_id,
            embedding_backend=entity.embedding_backend,
            embedding_model=entity.embedding_model,
            embedding_api_key_credential_id=entity.embedding_api_key_credential_id,
            llm_backend=entity.llm_backend,
            llm_model=entity.llm_model,
            llm_api_key_credential_id=entity.llm_api_key_credential_id,
            chunking_strategy=entity.chunking_strategy,
            parent_child_chunking=entity.parent_child_chunking,
            retrieval_strategy=entity.retrieval_strategy,
            retrieval_top_k=entity.retrieval_top_k,
            retrieval_min_score=entity.retrieval_min_score,
            reranking_enabled=entity.reranking_enabled,
            reranker_backend=entity.reranker_backend,
            reranker_model=entity.reranker_model,
            reranker_candidate_multiplier=entity.reranker_candidate_multiplier,
            chat_history_window_size=entity.chat_history_window_size,
            chat_history_max_chars=entity.chat_history_max_chars,
        )
