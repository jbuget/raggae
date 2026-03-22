from uuid import UUID

from raggae.application.dto.organization_default_config_dto import OrganizationDefaultConfigDTO
from raggae.application.interfaces.repositories.organization_default_config_repository import (
    OrganizationDefaultConfigRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class GetOrganizationDefaultConfig:
    """Use Case: Get default assistant config for an organization (OWNER or MAKER)."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        organization_default_config_repository: OrganizationDefaultConfigRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._organization_default_config_repository = organization_default_config_repository

    async def execute(self, organization_id: UUID, user_id: UUID) -> OrganizationDefaultConfigDTO | None:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        member = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None or member.role == OrganizationMemberRole.USER:
            raise OrganizationAccessDeniedError(
                f"User {user_id} cannot access config for organization {organization_id}"
            )
        config = await self._organization_default_config_repository.find_by_organization_id(organization_id)
        if config is None:
            return None
        return OrganizationDefaultConfigDTO.from_entity(config)
