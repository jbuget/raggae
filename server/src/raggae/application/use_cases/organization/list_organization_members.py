from uuid import UUID

from raggae.application.dto.organization_member_dto import OrganizationMemberDTO
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


class ListOrganizationMembers:
    """Use Case: List members for an organization."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository

    async def execute(self, organization_id: UUID, user_id: UUID) -> list[OrganizationMemberDTO]:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        requester = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if requester is None:
            raise OrganizationAccessDeniedError(
                f"User {user_id} cannot access organization members for {organization_id}"
            )
        members = await self._organization_member_repository.find_by_organization_id(organization_id)
        return [OrganizationMemberDTO.from_entity(member) for member in members]
