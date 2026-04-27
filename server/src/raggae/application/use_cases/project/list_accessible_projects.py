from uuid import UUID

from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.entities.project import Project
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class ListAccessibleProjects:
    """Use Case: List all projects accessible to a user (personal + organization projects)."""

    def __init__(
        self,
        organization_member_repository: OrganizationMemberRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._organization_member_repository = organization_member_repository
        self._project_repository = project_repository

    async def execute(self, user_id: UUID) -> list[ProjectDTO]:
        personal_projects = await self._project_repository.find_by_user_id(user_id)

        memberships = await self._organization_member_repository.find_by_user_id(user_id)

        org_projects: list[Project] = []
        for membership in memberships:
            projects = await self._project_repository.find_by_organization_id(membership.organization_id)
            if membership.role == OrganizationMemberRole.USER:
                projects = [p for p in projects if p.is_published]
            org_projects.extend(projects)

        all_projects = [*personal_projects, *org_projects]
        return [ProjectDTO.from_entity(p) for p in all_projects]
