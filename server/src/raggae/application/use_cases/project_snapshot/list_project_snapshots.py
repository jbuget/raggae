from uuid import UUID

from raggae.application.dto.project_snapshot_dto import ProjectSnapshotDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.project_snapshot_repository import (
    ProjectSnapshotRepository,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class ListProjectSnapshots:
    """Use Case: List all snapshots for a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        snapshot_repository: ProjectSnapshotRepository,
        organization_member_repository: OrganizationMemberRepository | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._snapshot_repository = snapshot_repository
        self._organization_member_repository = organization_member_repository

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ProjectSnapshotDTO], int]:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        if project.user_id != user_id:
            if project.organization_id is None or self._organization_member_repository is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
            member = await self._organization_member_repository.find_by_organization_and_user(
                organization_id=project.organization_id,
                user_id=user_id,
            )
            if member is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
            if member.role not in {OrganizationMemberRole.OWNER, OrganizationMemberRole.MAKER}:
                if not project.is_published:
                    raise ProjectNotFoundError(f"Project {project_id} not found")

        snapshots = await self._snapshot_repository.find_by_project_id(
            project_id=project_id,
            limit=limit,
            offset=offset,
        )
        total = await self._snapshot_repository.count_by_project_id(project_id)

        return [ProjectSnapshotDTO.from_entity(s) for s in snapshots], total
