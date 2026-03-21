from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.domain.entities.project import Project
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


@dataclass(frozen=True)
class ProjectSnapshot:
    """Immutable snapshot of a Project configuration at a point in time.

    Encrypted API keys and transient reindex state are intentionally excluded.
    """

    id: UUID
    project_id: UUID
    version_number: int
    label: str | None
    created_at: datetime
    created_by_user_id: UUID

    # Project configuration fields (excluding encrypted keys and reindex state)
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
    def from_project(
        cls,
        project: Project,
        version_number: int,
        created_by_user_id: UUID,
        label: str | None = None,
        restored_from_version: int | None = None,
    ) -> "ProjectSnapshot":
        """Create a new ProjectSnapshot from a Project entity."""
        return cls(
            id=uuid4(),
            project_id=project.id,
            version_number=version_number,
            label=label,
            created_at=datetime.now(UTC),
            created_by_user_id=created_by_user_id,
            name=project.name,
            description=project.description,
            system_prompt=project.system_prompt,
            is_published=project.is_published,
            chunking_strategy=project.chunking_strategy,
            parent_child_chunking=project.parent_child_chunking,
            organization_id=project.organization_id,
            embedding_backend=project.embedding_backend,
            embedding_model=project.embedding_model,
            embedding_api_key_credential_id=project.embedding_api_key_credential_id,
            org_embedding_api_key_credential_id=project.org_embedding_api_key_credential_id,
            llm_backend=project.llm_backend,
            llm_model=project.llm_model,
            llm_api_key_credential_id=project.llm_api_key_credential_id,
            org_llm_api_key_credential_id=project.org_llm_api_key_credential_id,
            retrieval_strategy=project.retrieval_strategy,
            retrieval_top_k=project.retrieval_top_k,
            retrieval_min_score=project.retrieval_min_score,
            chat_history_window_size=project.chat_history_window_size,
            chat_history_max_chars=project.chat_history_max_chars,
            reranking_enabled=project.reranking_enabled,
            reranker_backend=project.reranker_backend,
            reranker_model=project.reranker_model,
            reranker_candidate_multiplier=project.reranker_candidate_multiplier,
            restored_from_version=restored_from_version,
        )
