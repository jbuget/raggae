from uuid import UUID

from raggae.application.dto.project_snapshot_dto import ProjectSnapshotDTO
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.project_snapshot_repository import (
    ProjectSnapshotRepository,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class ListProjectSnapshots:
    """Use Case: List all snapshots for a project."""

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
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ProjectSnapshotDTO]:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        if project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        snapshots = await self._snapshot_repository.find_by_project_id(
            project_id=project_id,
            limit=limit,
            offset=offset,
        )

        return [ProjectSnapshotDTO.from_entity(s) for s in snapshots]
