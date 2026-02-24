from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.organization_member_dto import OrganizationMemberDTO
from raggae.application.interfaces.repositories.organization_invitation_repository import (
    OrganizationInvitationRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationInvitationInvalidError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)


class AcceptUserOrganizationInvitation:
    """Use Case: Accept a pending organization invitation for the current user."""

    def __init__(
        self,
        user_repository: UserRepository,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        organization_invitation_repository: OrganizationInvitationRepository,
    ) -> None:
        self._user_repository = user_repository
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._organization_invitation_repository = organization_invitation_repository

    async def execute(self, invitation_id: UUID, user_id: UUID) -> OrganizationMemberDTO:
        invitation = await self._organization_invitation_repository.find_by_id(invitation_id)
        if invitation is None:
            raise OrganizationInvitationInvalidError("Invitation not found")

        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise OrganizationInvitationInvalidError("Invitation not found")

        if invitation.email.strip().lower() != user.email.strip().lower():
            raise OrganizationInvitationInvalidError("Invitation not found")

        organization = await self._organization_repository.find_by_id(invitation.organization_id)
        if organization is None:
            raise OrganizationNotFoundError(
                f"Organization {invitation.organization_id} not found"
            )

        now = datetime.now(UTC)
        if invitation.status != OrganizationInvitationStatus.PENDING:
            raise OrganizationInvitationInvalidError("Invitation is not pending")
        if invitation.expires_at < now:
            expired = invitation.with_status(
                status=OrganizationInvitationStatus.EXPIRED,
                updated_at=now,
            )
            await self._organization_invitation_repository.save(expired)
            raise OrganizationInvitationInvalidError("Invitation is expired")

        existing = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=invitation.organization_id,
            user_id=user_id,
        )
        if existing is not None:
            accepted = invitation.with_status(
                status=OrganizationInvitationStatus.ACCEPTED,
                updated_at=now,
            )
            await self._organization_invitation_repository.save(accepted)
            return OrganizationMemberDTO.from_entity(existing)

        member = OrganizationMember(
            id=uuid4(),
            organization_id=invitation.organization_id,
            user_id=user_id,
            role=invitation.role,
            joined_at=now,
        )
        accepted = invitation.with_status(
            status=OrganizationInvitationStatus.ACCEPTED,
            updated_at=now,
        )
        await self._organization_member_repository.save(member)
        await self._organization_invitation_repository.save(accepted)
        return OrganizationMemberDTO.from_entity(member)
