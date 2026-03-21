from uuid import UUID

from raggae.application.dto.project_snapshot_dto import ProjectSnapshotDTO
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.project_snapshot_repository import (
    ProjectSnapshotRepository,
)
from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class CreateProjectSnapshot:
    """Use Case: Create a configuration snapshot for a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        snapshot_repository: ProjectSnapshotRepository,
    ) -> None:
        self._project_repository = project_repository
        self._snapshot_repository = snapshot_repository

    async def execute(
        self,
        project_id: UUID,
        created_by_user_id: UUID,
        label: str | None = None,
        restored_from_version: int | None = None,
    ) -> ProjectSnapshotDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        version_number = await self._snapshot_repository.get_next_version_number(project_id)

        snapshot = ProjectSnapshot.from_project(
            project=project,
            version_number=version_number,
            created_by_user_id=created_by_user_id,
            label=label,
            restored_from_version=restored_from_version,
        )

        await self._snapshot_repository.save(snapshot)

        return ProjectSnapshotDTO.from_entity(snapshot)
