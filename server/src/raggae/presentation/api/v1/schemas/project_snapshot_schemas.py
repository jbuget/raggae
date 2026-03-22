from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class ProjectSnapshotResponse(BaseModel):
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
    retrieval_strategy: Literal["vector", "fulltext", "hybrid"]
    retrieval_top_k: int
    retrieval_min_score: float
    chat_history_window_size: int
    chat_history_max_chars: int
    reranking_enabled: bool
    reranker_backend: Literal["none", "cross_encoder", "inmemory", "mmr"] | None
    reranker_model: str | None
    reranker_candidate_multiplier: int
    restored_from_version: int | None


class ProjectSnapshotListResponse(BaseModel):
    snapshots: list[ProjectSnapshotResponse]
    total: int
    limit: int
    offset: int
