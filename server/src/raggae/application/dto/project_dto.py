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

    @classmethod
    def from_entity(cls, project: Project) -> "ProjectDTO":
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
        )
