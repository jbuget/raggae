from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.project import Project
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


@dataclass
class ProjectDTO:
    """Data Transfer Object for Project."""

    id: UUID
    user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    created_at: datetime
    chunking_strategy: ChunkingStrategy
    parent_child_chunking: bool
    reindex_status: str
    reindex_progress: int
    reindex_total: int
    embedding_backend: str | None
    embedding_model: str | None
    embedding_api_key_masked: str | None
    embedding_api_key_credential_id: UUID | None
    llm_backend: str | None
    llm_model: str | None
    llm_api_key_masked: str | None
    llm_api_key_credential_id: UUID | None
    retrieval_strategy: str
    retrieval_top_k: int
    retrieval_min_score: float
    chat_history_window_size: int
    chat_history_max_chars: int
    reranking_enabled: bool
    reranker_backend: str | None
    reranker_model: str | None
    reranker_candidate_multiplier: int

    @classmethod
    def from_entity(cls, project: Project) -> "ProjectDTO":
        embedding_masked = (
            f"...{project.embedding_api_key_encrypted[-4:]}"
            if project.embedding_api_key_encrypted
            else None
        )
        llm_masked = (
            f"...{project.llm_api_key_encrypted[-4:]}" if project.llm_api_key_encrypted else None
        )
        return cls(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            system_prompt=project.system_prompt,
            is_published=project.is_published,
            created_at=project.created_at,
            chunking_strategy=project.chunking_strategy,
            parent_child_chunking=project.parent_child_chunking,
            reindex_status=project.reindex_status,
            reindex_progress=project.reindex_progress,
            reindex_total=project.reindex_total,
            embedding_backend=project.embedding_backend,
            embedding_model=project.embedding_model,
            embedding_api_key_masked=embedding_masked,
            embedding_api_key_credential_id=project.embedding_api_key_credential_id,
            llm_backend=project.llm_backend,
            llm_model=project.llm_model,
            llm_api_key_masked=llm_masked,
            llm_api_key_credential_id=project.llm_api_key_credential_id,
            retrieval_strategy=project.retrieval_strategy,
            retrieval_top_k=project.retrieval_top_k,
            retrieval_min_score=project.retrieval_min_score,
            chat_history_window_size=project.chat_history_window_size,
            chat_history_max_chars=project.chat_history_max_chars,
            reranking_enabled=project.reranking_enabled,
            reranker_backend=project.reranker_backend,
            reranker_model=project.reranker_model,
            reranker_candidate_multiplier=project.reranker_candidate_multiplier,
        )
