from datetime import UTC, datetime
from uuid import UUID

from raggae.application.dto.organization_dto import OrganizationDTO
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


class UpdateOrganization:
    """Use Case: Update organization profile (owner only)."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository

    async def execute(
        self,
        organization_id: UUID,
        user_id: UUID,
        name: str,
        slug: str | None,
        description: str | None,
        logo_url: str | None,
    ) -> OrganizationDTO:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        member = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None or member.role != OrganizationMemberRole.OWNER:
            raise OrganizationAccessDeniedError(
                f"User {user_id} cannot update organization {organization_id}"
            )
        updated = organization.update_profile(
            name=name,
            slug=slug,
            description=description,
            logo_url=logo_url,
            updated_at=datetime.now(UTC),
        )
        await self._organization_repository.save(updated)
        return OrganizationDTO.from_entity(updated)
