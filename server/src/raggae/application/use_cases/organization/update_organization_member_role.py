from uuid import UUID

from raggae.application.dto.organization_member_dto import OrganizationMemberDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.domain.entities.organization import Organization
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class UpdateOrganizationMemberRole:
    """Use Case: Update member role (owner only)."""

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
        requester_user_id: UUID,
        member_id: UUID,
        role: OrganizationMemberRole,
    ) -> OrganizationMemberDTO:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        requester = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=requester_user_id,
        )
        if requester is None or requester.role != OrganizationMemberRole.OWNER:
            raise OrganizationAccessDeniedError(
                f"User {requester_user_id} cannot update members in organization {organization_id}"
            )

        target = await self._organization_member_repository.find_by_id(member_id)
        if target is None or target.organization_id != organization_id:
            raise OrganizationNotFoundError(f"Member {member_id} not found in organization")

        members = await self._organization_member_repository.find_by_organization_id(
            organization_id
        )
        Organization.ensure_can_change_role(target_member=target, next_role=role, members=members)
        updated = target.with_role(role)
        await self._organization_member_repository.save(updated)
        return OrganizationMemberDTO.from_entity(updated)
