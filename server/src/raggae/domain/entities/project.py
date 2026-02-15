from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from raggae.domain.exceptions.project_exceptions import ProjectAlreadyPublishedError


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

    def publish(self) -> "Project":
        """Publish the project. Raises if already published."""
        if self.is_published:
            raise ProjectAlreadyPublishedError()
        return replace(self, is_published=True)

    def update_prompt(self, new_prompt: str) -> "Project":
        """Return a new Project with an updated system prompt."""
        return replace(self, system_prompt=new_prompt)
