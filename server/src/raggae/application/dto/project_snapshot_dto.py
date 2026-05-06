from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.project_snapshot import ProjectSnapshot


@dataclass
class ProjectSnapshotDTO:
    """Data Transfer Object for ProjectSnapshot."""

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
    def from_entity(cls, snapshot: ProjectSnapshot) -> "ProjectSnapshotDTO":
        return cls(
            id=snapshot.id,
            project_id=snapshot.project_id,
            version_number=snapshot.version_number,
            label=snapshot.label,
            created_at=snapshot.created_at,
            created_by_user_id=snapshot.created_by_user_id,
            name=snapshot.name,
            description=snapshot.description,
            system_prompt=snapshot.system_prompt,
            is_published=snapshot.is_published,
            organization_id=snapshot.organization_id,
            restored_from_version=snapshot.restored_from_version,
        )
