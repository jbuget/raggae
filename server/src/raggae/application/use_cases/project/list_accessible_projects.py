from uuid import UUID

from raggae.application.dto.accessible_projects_dto import AccessibleProjectsDTO, OrganizationSectionDTO
from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.organization_member_repository import OrganizationMemberRepository
from raggae.application.interfaces.repositories.organization_repository import OrganizationRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class ListAccessibleProjects:
    """Use Case: List all projects accessible to a user (personal + organization projects)."""

    def __init__(
        self,
        organization_member_repository: OrganizationMemberRepository,
        organization_repository: OrganizationRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._organization_member_repository = organization_member_repository
        self._organization_repository = organization_repository
        self._project_repository = project_repository

    async def execute(self, user_id: UUID) -> AccessibleProjectsDTO:
        personal_projects = await self._project_repository.find_by_user_id(user_id)
        memberships = await self._organization_member_repository.find_by_user_id(user_id)

        if not memberships:
            return AccessibleProjectsDTO(
                personal_projects=[ProjectDTO.from_entity(p) for p in personal_projects],
                organization_sections=[],
            )

        org_ids = [m.organization_id for m in memberships]
        all_org_projects = await self._project_repository.find_by_organization_ids(org_ids)

        projects_by_org: dict[UUID, list] = {org_id: [] for org_id in org_ids}
        for project in all_org_projects:
            if project.organization_id in projects_by_org:
                projects_by_org[project.organization_id].append(project)

        organization_sections: list[OrganizationSectionDTO] = []
        for membership in memberships:
            org = await self._organization_repository.find_by_id(membership.organization_id)
            if org is None:
                continue
            projects = projects_by_org.get(membership.organization_id, [])
            if membership.role == OrganizationMemberRole.USER:
                projects = [p for p in projects if p.is_published]
            can_edit = membership.role in (OrganizationMemberRole.OWNER, OrganizationMemberRole.MAKER)
            organization_sections.append(
                OrganizationSectionDTO(
                    organization_id=org.id,
                    organization_name=org.name,
                    projects=[ProjectDTO.from_entity(p) for p in projects],
                    can_edit=can_edit,
                )
            )

        return AccessibleProjectsDTO(
            personal_projects=[ProjectDTO.from_entity(p) for p in personal_projects],
            organization_sections=organization_sections,
        )
