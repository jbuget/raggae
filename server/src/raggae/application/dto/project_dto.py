from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.project import Project


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
        )
