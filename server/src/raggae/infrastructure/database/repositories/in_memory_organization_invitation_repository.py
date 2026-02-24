from uuid import UUID

from raggae.domain.entities.organization_invitation import OrganizationInvitation
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)


class InMemoryOrganizationInvitationRepository:
    """In-memory organization invitation repository for testing."""

    def __init__(self) -> None:
        self._invitations: dict[UUID, OrganizationInvitation] = {}

    async def save(self, invitation: OrganizationInvitation) -> None:
        self._invitations[invitation.id] = invitation

    async def find_by_id(self, invitation_id: UUID) -> OrganizationInvitation | None:
        return self._invitations.get(invitation_id)

    async def find_by_token_hash(self, token_hash: str) -> OrganizationInvitation | None:
        for invitation in self._invitations.values():
            if invitation.token_hash == token_hash:
                return invitation
        return None

    async def find_pending_by_organization_and_email(
        self, organization_id: UUID, email: str
    ) -> OrganizationInvitation | None:
        normalized_email = email.strip().lower()
        for invitation in self._invitations.values():
            if (
                invitation.organization_id == organization_id
                and invitation.email.strip().lower() == normalized_email
                and invitation.status == OrganizationInvitationStatus.PENDING
            ):
                return invitation
        return None

    async def find_by_organization_id(self, organization_id: UUID) -> list[OrganizationInvitation]:
        return [i for i in self._invitations.values() if i.organization_id == organization_id]

    async def find_pending_by_email(self, email: str) -> list[OrganizationInvitation]:
        normalized_email = email.strip().lower()
        return [
            invitation
            for invitation in self._invitations.values()
            if invitation.email.strip().lower() == normalized_email
            and invitation.status == OrganizationInvitationStatus.PENDING
        ]

    async def delete_by_organization_id(self, organization_id: UUID) -> None:
        invitation_ids = [
            invitation.id
            for invitation in self._invitations.values()
            if invitation.organization_id == organization_id
        ]
        for invitation_id in invitation_ids:
            self._invitations.pop(invitation_id, None)
