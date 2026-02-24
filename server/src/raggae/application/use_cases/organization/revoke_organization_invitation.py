from datetime import UTC, datetime
from uuid import UUID

from raggae.application.dto.organization_invitation_dto import OrganizationInvitationDTO
from raggae.application.interfaces.repositories.organization_invitation_repository import (
    OrganizationInvitationRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationInvitationInvalidError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class RevokeOrganizationInvitation:
    """Use Case: Revoke organization invitation (owner only)."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        organization_invitation_repository: OrganizationInvitationRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._organization_invitation_repository = organization_invitation_repository

    async def execute(
        self, organization_id: UUID, requester_user_id: UUID, invitation_id: UUID
    ) -> OrganizationInvitationDTO:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        requester = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=requester_user_id,
        )
        if requester is None or requester.role != OrganizationMemberRole.OWNER:
            raise OrganizationAccessDeniedError(
                f"User {requester_user_id} cannot revoke invitation in organization {organization_id}"
            )
        invitation = await self._organization_invitation_repository.find_by_id(invitation_id)
        if invitation is None or invitation.organization_id != organization_id:
            raise OrganizationInvitationInvalidError(
                f"Invitation {invitation_id} not found in organization {organization_id}"
            )
        revoked = invitation.with_status(
            status=OrganizationInvitationStatus.REVOKED,
            updated_at=datetime.now(UTC),
        )
        await self._organization_invitation_repository.save(revoked)
        return OrganizationInvitationDTO.from_entity(revoked)
