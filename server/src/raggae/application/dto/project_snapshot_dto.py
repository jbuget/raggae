from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


@dataclass
class ProjectSnapshotDTO:
    """Data Transfer Object for ProjectSnapshot."""

    id: UUID
    project_id: UUID
    version_number: int
    label: str | None
    created_at: datetime
    created_by_user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    chunking_strategy: ChunkingStrategy
    parent_child_chunking: bool
    organization_id: UUID | None
    embedding_backend: str | None
    embedding_model: str | None
    embedding_api_key_credential_id: UUID | None
    org_embedding_api_key_credential_id: UUID | None
    llm_backend: str | None
    llm_model: str | None
    llm_api_key_credential_id: UUID | None
    org_llm_api_key_credential_id: UUID | None
    retrieval_strategy: str
    retrieval_top_k: int
    retrieval_min_score: float
    chat_history_window_size: int
    chat_history_max_chars: int
    reranking_enabled: bool
    reranker_backend: str | None
    reranker_model: str | None
    reranker_candidate_multiplier: int
    restored_from_version: int | None

    @classmethod
    def from_entity(cls, snapshot: ProjectSnapshot) -> "ProjectSnapshotDTO":
        return cls(
            id=snapshot.id,
            project_id=snapshot.project_id,
            version_number=snapshot.version_number,
            label=snapshot.label,
            created_at=snapshot.created_at,
            created_by_user_id=snapshot.created_by_user_id,
            name=snapshot.name,
            description=snapshot.description,
            system_prompt=snapshot.system_prompt,
            is_published=snapshot.is_published,
            chunking_strategy=snapshot.chunking_strategy,
            parent_child_chunking=snapshot.parent_child_chunking,
            organization_id=snapshot.organization_id,
            embedding_backend=snapshot.embedding_backend,
            embedding_model=snapshot.embedding_model,
            embedding_api_key_credential_id=snapshot.embedding_api_key_credential_id,
            org_embedding_api_key_credential_id=snapshot.org_embedding_api_key_credential_id,
            llm_backend=snapshot.llm_backend,
            llm_model=snapshot.llm_model,
            llm_api_key_credential_id=snapshot.llm_api_key_credential_id,
            org_llm_api_key_credential_id=snapshot.org_llm_api_key_credential_id,
            retrieval_strategy=snapshot.retrieval_strategy,
            retrieval_top_k=snapshot.retrieval_top_k,
            retrieval_min_score=snapshot.retrieval_min_score,
            chat_history_window_size=snapshot.chat_history_window_size,
            chat_history_max_chars=snapshot.chat_history_max_chars,
            reranking_enabled=snapshot.reranking_enabled,
            reranker_backend=snapshot.reranker_backend,
            reranker_model=snapshot.reranker_model,
            reranker_candidate_multiplier=snapshot.reranker_candidate_multiplier,
            restored_from_version=snapshot.restored_from_version,
        )
