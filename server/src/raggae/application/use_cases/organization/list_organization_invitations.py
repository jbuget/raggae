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
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class ListOrganizationInvitations:
    """Use Case: List organization invitations (owner only)."""

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
        self, organization_id: UUID, requester_user_id: UUID
    ) -> list[OrganizationInvitationDTO]:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        requester = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=requester_user_id,
        )
        if requester is None or requester.role != OrganizationMemberRole.OWNER:
            raise OrganizationAccessDeniedError(
                f"User {requester_user_id} cannot list invitations for organization {organization_id}"
            )
        invitations = await self._organization_invitation_repository.find_by_organization_id(
            organization_id
        )
        return [
            OrganizationInvitationDTO.from_entity(invitation)
            for invitation in invitations
            if invitation.status == OrganizationInvitationStatus.PENDING
        ]
