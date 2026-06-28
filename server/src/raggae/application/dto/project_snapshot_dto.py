from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.project_snapshot import ProjectSnapshot


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
    organization_id: UUID | None
    restored_from_version: int | None
    embedding_backend: str | None = field(default=None)
    embedding_model: str | None = field(default=None)
    embedding_api_key_credential_id: UUID | None = field(default=None)
    llm_backend: str | None = field(default=None)
    llm_model: str | None = field(default=None)
    llm_api_key_credential_id: UUID | None = field(default=None)
    chunking_strategy: str | None = field(default=None)
    parent_child_chunking: bool | None = field(default=None)
    retrieval_strategy: str | None = field(default=None)
    retrieval_top_k: int | None = field(default=None)
    retrieval_min_score: float | None = field(default=None)
    reranking_enabled: bool | None = field(default=None)
    reranker_backend: str | None = field(default=None)
    reranker_model: str | None = field(default=None)
    reranker_candidate_multiplier: int | None = field(default=None)
    chat_history_window_size: int | None = field(default=None)
    chat_history_max_chars: int | None = field(default=None)

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
            organization_id=snapshot.organization_id,
            restored_from_version=snapshot.restored_from_version,
            embedding_backend=snapshot.embedding_backend,
            embedding_model=snapshot.embedding_model,
            embedding_api_key_credential_id=snapshot.embedding_api_key_credential_id,
            llm_backend=snapshot.llm_backend,
            llm_model=snapshot.llm_model,
            llm_api_key_credential_id=snapshot.llm_api_key_credential_id,
            chunking_strategy=snapshot.chunking_strategy,
            parent_child_chunking=snapshot.parent_child_chunking,
            retrieval_strategy=snapshot.retrieval_strategy,
            retrieval_top_k=snapshot.retrieval_top_k,
            retrieval_min_score=snapshot.retrieval_min_score,
            reranking_enabled=snapshot.reranking_enabled,
            reranker_backend=snapshot.reranker_backend,
            reranker_model=snapshot.reranker_model,
            reranker_candidate_multiplier=snapshot.reranker_candidate_multiplier,
            chat_history_window_size=snapshot.chat_history_window_size,
            chat_history_max_chars=snapshot.chat_history_max_chars,
        )
