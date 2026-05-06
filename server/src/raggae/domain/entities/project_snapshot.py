from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.domain.entities.project import Project


@dataclass(frozen=True)
class ProjectSnapshot:
    """Immutable snapshot of a Project at a point in time.

    Only captures the project's identity fields (name, description, system_prompt).
    Agent configuration is managed separately via agent_configurations.
    """

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

    @classmethod
    def from_project(
        cls,
        project: Project,
        version_number: int,
        created_by_user_id: UUID,
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
        )
