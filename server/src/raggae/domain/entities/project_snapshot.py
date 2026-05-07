from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.domain.entities.project import Project


@dataclass(frozen=True)
class ProjectSnapshot:
    """Immutable snapshot of a Project and its agent configuration at a point in time."""

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
    # Agent configuration captured at snapshot time
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
    def from_project(
        cls,
        project: Project,
        version_number: int,
        created_by_user_id: UUID,
        agent_config: object | None = None,
        label: str | None = None,
        restored_from_version: int | None = None,
    ) -> "ProjectSnapshot":
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
            organization_id=project.organization_id,
            restored_from_version=restored_from_version,
            embedding_backend=agent_config.embedding_backend if agent_config else None,
            embedding_model=agent_config.embedding_model if agent_config else None,
            embedding_api_key_credential_id=agent_config.embedding_api_key_credential_id if agent_config else None,
            llm_backend=agent_config.llm_backend if agent_config else None,
            llm_model=agent_config.llm_model if agent_config else None,
            llm_api_key_credential_id=agent_config.llm_api_key_credential_id if agent_config else None,
            chunking_strategy=agent_config.chunking_strategy if agent_config else None,
            parent_child_chunking=agent_config.parent_child_chunking if agent_config else None,
            retrieval_strategy=agent_config.retrieval_strategy if agent_config else None,
            retrieval_top_k=agent_config.retrieval_top_k if agent_config else None,
            retrieval_min_score=agent_config.retrieval_min_score if agent_config else None,
            reranking_enabled=agent_config.reranking_enabled if agent_config else None,
            reranker_backend=agent_config.reranker_backend if agent_config else None,
            reranker_model=agent_config.reranker_model if agent_config else None,
            reranker_candidate_multiplier=agent_config.reranker_candidate_multiplier if agent_config else None,
            chat_history_window_size=agent_config.chat_history_window_size if agent_config else None,
            chat_history_max_chars=agent_config.chat_history_max_chars if agent_config else None,
        )
