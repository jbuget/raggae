from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.organization_default_config import OrganizationDefaultConfig
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


@dataclass
class OrganizationDefaultConfigDTO:
    """Data Transfer Object for OrganizationDefaultConfig."""

    id: UUID
    organization_id: UUID
    embedding_backend: str | None
    embedding_model: str | None
    llm_backend: str | None
    llm_model: str | None
    chunking_strategy: ChunkingStrategy | None
    parent_child_chunking: bool | None
    retrieval_strategy: str | None
    retrieval_top_k: int | None
    retrieval_min_score: float | None
    reranking_enabled: bool | None
    reranker_backend: str | None
    reranker_model: str | None
    reranker_candidate_multiplier: int | None
    org_embedding_api_key_credential_id: UUID | None
    org_llm_api_key_credential_id: UUID | None
    updated_at: datetime

    @classmethod
    def from_entity(cls, config: OrganizationDefaultConfig) -> "OrganizationDefaultConfigDTO":
        return cls(
            id=config.id,
            organization_id=config.organization_id,
            embedding_backend=config.embedding_backend,
            embedding_model=config.embedding_model,
            llm_backend=config.llm_backend,
            llm_model=config.llm_model,
            chunking_strategy=config.chunking_strategy,
            parent_child_chunking=config.parent_child_chunking,
            retrieval_strategy=config.retrieval_strategy,
            retrieval_top_k=config.retrieval_top_k,
            retrieval_min_score=config.retrieval_min_score,
            reranking_enabled=config.reranking_enabled,
            reranker_backend=config.reranker_backend,
            reranker_model=config.reranker_model,
            reranker_candidate_multiplier=config.reranker_candidate_multiplier,
            org_embedding_api_key_credential_id=config.org_embedding_api_key_credential_id,
            org_llm_api_key_credential_id=config.org_llm_api_key_credential_id,
            updated_at=config.updated_at,
        )
