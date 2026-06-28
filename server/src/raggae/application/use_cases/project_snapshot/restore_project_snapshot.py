from dataclasses import replace
from uuid import UUID

from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.project_snapshot_repository import (
    ProjectSnapshotRepository,
)
from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.exceptions.project_snapshot_exceptions import ProjectSnapshotNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class RestoreProjectSnapshot:
    """Use Case: Restore a project to a previous snapshot version.

    Applies the snapshot's name/description/system_prompt/is_published to the project.
    Agent configuration is not restored (managed separately via agent_configurations).
    """

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
        version_number: int,
        user_id: UUID,
    ) -> ProjectDTO:
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
                raise ProjectNotFoundError(f"Project {project_id} not found")

        snapshot = await self._snapshot_repository.find_by_project_and_version(
            project_id=project_id,
            version_number=version_number,
        )
        if snapshot is None:
            raise ProjectSnapshotNotFoundError(
                f"Snapshot version {version_number} not found for project {project_id}"
            )

        restored_project = replace(
            project,
            name=snapshot.name,
            description=snapshot.description,
            system_prompt=snapshot.system_prompt,
            is_published=snapshot.is_published,
        )
        await self._project_repository.save(restored_project)

        next_version = await self._snapshot_repository.get_next_version_number(project_id)
        restore_snapshot = ProjectSnapshot.from_project(
            project=restored_project,
            version_number=next_version,
            created_by_user_id=user_id,
            restored_from_version=version_number,
        )
        await self._snapshot_repository.save(restore_snapshot)

        return ProjectDTO.from_entity(restored_project)
