from datetime import UTC, datetime
from uuid import UUID

from raggae.application.dto.user_pending_organization_invitation_dto import (
    UserPendingOrganizationInvitationDTO,
)
from raggae.application.interfaces.repositories.organization_invitation_repository import (
    OrganizationInvitationRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)


class ListUserPendingOrganizationInvitations:
    """Use Case: List pending organization invitations for the current user."""

    def __init__(
        self,
        user_repository: UserRepository,
        organization_repository: OrganizationRepository,
        organization_invitation_repository: OrganizationInvitationRepository,
    ) -> None:
        self._user_repository = user_repository
        self._organization_repository = organization_repository
        self._organization_invitation_repository = organization_invitation_repository

    async def execute(self, user_id: UUID) -> list[UserPendingOrganizationInvitationDTO]:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            return []

        now = datetime.now(UTC)
        invitations = await self._organization_invitation_repository.find_pending_by_email(
            user.email
        )
        pending_invitations: list[UserPendingOrganizationInvitationDTO] = []
        for invitation in invitations:
            if invitation.expires_at < now:
                expired = invitation.with_status(
                    status=OrganizationInvitationStatus.EXPIRED,
                    updated_at=now,
                )
                await self._organization_invitation_repository.save(expired)
                continue
            organization = await self._organization_repository.find_by_id(invitation.organization_id)
            if organization is None:
                continue
            pending_invitations.append(
                UserPendingOrganizationInvitationDTO.from_entity(
                    invitation=invitation,
                    organization_name=organization.name,
                )
            )

        return sorted(pending_invitations, key=lambda invitation: invitation.created_at, reverse=True)
