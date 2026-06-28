from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
    organization_id: UUID | None
    restored_from_version: int | None
    embedding_backend: str | None = None
    embedding_model: str | None = None
    llm_backend: str | None = None
    llm_model: str | None = None
    chunking_strategy: str | None = None
    parent_child_chunking: bool | None = None
    retrieval_strategy: str | None = None
    retrieval_top_k: int | None = None
    retrieval_min_score: float | None = None
    reranking_enabled: bool | None = None
    reranker_backend: str | None = None
    reranker_model: str | None = None
    reranker_candidate_multiplier: int | None = None
    chat_history_window_size: int | None = None
    chat_history_max_chars: int | None = None


class ProjectSnapshotListResponse(BaseModel):
    snapshots: list[ProjectSnapshotResponse]
    total: int
    limit: int
    offset: int
