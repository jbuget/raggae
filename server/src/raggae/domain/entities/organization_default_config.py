from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


@dataclass(frozen=True)
class OrganizationDefaultConfig:
    """Default assistant configuration for an organization."""

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

    def update(
        self,
        embedding_backend: str | None,
        embedding_model: str | None,
        llm_backend: str | None,
        llm_model: str | None,
        chunking_strategy: ChunkingStrategy | None,
        parent_child_chunking: bool | None,
        retrieval_strategy: str | None,
        retrieval_top_k: int | None,
        retrieval_min_score: float | None,
        reranking_enabled: bool | None,
        reranker_backend: str | None,
        reranker_model: str | None,
        reranker_candidate_multiplier: int | None,
        org_embedding_api_key_credential_id: UUID | None,
        org_llm_api_key_credential_id: UUID | None,
        updated_at: datetime,
    ) -> "OrganizationDefaultConfig":
        """Return a new config with updated fields."""
        return replace(
            self,
            embedding_backend=embedding_backend,
            embedding_model=embedding_model,
            llm_backend=llm_backend,
            llm_model=llm_model,
            chunking_strategy=chunking_strategy,
            parent_child_chunking=parent_child_chunking,
            retrieval_strategy=retrieval_strategy,
            retrieval_top_k=retrieval_top_k,
            retrieval_min_score=retrieval_min_score,
            reranking_enabled=reranking_enabled,
            reranker_backend=reranker_backend,
            reranker_model=reranker_model,
            reranker_candidate_multiplier=reranker_candidate_multiplier,
            org_embedding_api_key_credential_id=org_embedding_api_key_credential_id,
            org_llm_api_key_credential_id=org_llm_api_key_credential_id,
            updated_at=updated_at,
        )
