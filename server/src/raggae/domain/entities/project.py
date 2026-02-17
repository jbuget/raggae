from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from raggae.domain.exceptions.project_exceptions import ProjectAlreadyPublishedError
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

    def publish(self) -> "Project":
        """Publish the project. Raises if already published."""
        if self.is_published:
            raise ProjectAlreadyPublishedError()
        return replace(self, is_published=True)

    def update_prompt(self, new_prompt: str) -> "Project":
        """Return a new Project with an updated system prompt."""
        return replace(self, system_prompt=new_prompt)
