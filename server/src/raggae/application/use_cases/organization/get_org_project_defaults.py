from uuid import UUID

from raggae.application.dto.project_defaults_dto import ProjectDefaultsDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.application.interfaces.repositories.project_defaults_repository import (
    ProjectDefaultsRepository,
)
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.project_defaults_owner_type import ProjectDefaultsOwnerType


class GetOrganizationProjectDefaults:
    """Use Case: Get the project defaults configured at organization level."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        project_defaults_repository: ProjectDefaultsRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._project_defaults_repository = project_defaults_repository

    async def execute(self, organization_id: UUID, user_id: UUID) -> ProjectDefaultsDTO | None:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        member = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None:
            raise OrganizationAccessDeniedError(
                f"User {user_id} is not a member of organization {organization_id}"
            )
        defaults = await self._project_defaults_repository.find_by_owner(
            organization_id, ProjectDefaultsOwnerType.ORGA
        )
        if defaults is None:
            return None
        return ProjectDefaultsDTO.from_entity(defaults)
