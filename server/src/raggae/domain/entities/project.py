from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from raggae.domain.exceptions.project_exceptions import (
    ProjectAlreadyPublishedError,
    ProjectReindexInProgressError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


@dataclass(frozen=True)
class Project:
    """Project domain entity. Immutable."""

    id: UUID
    user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    created_at: datetime
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.AUTO
    parent_child_chunking: bool = False
    reindex_status: str = "idle"
    reindex_progress: int = 0
    reindex_total: int = 0
    embedding_backend: str | None = None
    embedding_model: str | None = None
    embedding_api_key_encrypted: str | None = None
    embedding_api_key_credential_id: UUID | None = None
    llm_backend: str | None = None
    llm_model: str | None = None
    llm_api_key_encrypted: str | None = None
    llm_api_key_credential_id: UUID | None = None
    retrieval_strategy: str = "hybrid"
    retrieval_top_k: int = 8
    retrieval_min_score: float = 0.3
    chat_history_window_size: int = 8
    chat_history_max_chars: int = 4000

    def publish(self) -> "Project":
        """Publish the project. Raises if already published."""
        if self.is_published:
            raise ProjectAlreadyPublishedError()
        return replace(self, is_published=True)

    def update_prompt(self, new_prompt: str) -> "Project":
        """Return a new Project with an updated system prompt."""
        return replace(self, system_prompt=new_prompt)

    def start_reindex(self, total_documents: int) -> "Project":
        """Mark project as being reindexed and initialize progress."""
        if self.is_reindexing():
            raise ProjectReindexInProgressError("Project reindex is already in progress")
        total = max(0, total_documents)
        return replace(self, reindex_status="in_progress", reindex_progress=0, reindex_total=total)

    def advance_reindex(self) -> "Project":
        """Advance reindex progress by one document."""
        if not self.is_reindexing():
            return self
        progress = min(self.reindex_progress + 1, max(0, self.reindex_total))
        return replace(self, reindex_progress=progress)

    def finish_reindex(self) -> "Project":
        """Mark reindex as finished and keep final counters."""
        total = max(0, self.reindex_total)
        progress = min(max(0, self.reindex_progress), total)
        return replace(self, reindex_status="idle", reindex_progress=progress, reindex_total=total)

    def is_reindexing(self) -> bool:
        """Whether project is currently being reindexed."""
        return self.reindex_status == "in_progress"
