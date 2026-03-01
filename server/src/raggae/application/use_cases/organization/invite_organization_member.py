from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

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
from raggae.domain.entities.organization_invitation import OrganizationInvitation
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationInvitationInvalidError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class InviteOrganizationMember:
    """Use Case: Invite member in organization (owner only)."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        organization_invitation_repository: OrganizationInvitationRepository,
        invitation_ttl_days: int = 7,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._organization_invitation_repository = organization_invitation_repository
        self._invitation_ttl_days = invitation_ttl_days

    async def execute(
        self,
        organization_id: UUID,
        requester_user_id: UUID,
        email: str,
        role: OrganizationMemberRole,
    ) -> OrganizationInvitationDTO:
        await self._assert_owner(
            organization_id=organization_id, requester_user_id=requester_user_id
        )
        normalized_email = email.strip().lower()
        pending = (
            await self._organization_invitation_repository.find_pending_by_organization_and_email(
                organization_id=organization_id,
                email=normalized_email,
            )
        )
        if pending is not None:
            raise OrganizationInvitationInvalidError(
                f"Pending invitation already exists for {normalized_email}"
            )

        now = datetime.now(UTC)
        invitation = OrganizationInvitation(
            id=uuid4(),
            organization_id=organization_id,
            email=normalized_email,
            role=role,
            status=OrganizationInvitationStatus.PENDING,
            invited_by_user_id=requester_user_id,
            token_hash=uuid4().hex,
            expires_at=now + timedelta(days=self._invitation_ttl_days),
            created_at=now,
            updated_at=now,
        )
        await self._organization_invitation_repository.save(invitation)
        return OrganizationInvitationDTO.from_entity(invitation)

    async def _assert_owner(self, organization_id: UUID, requester_user_id: UUID) -> None:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        requester = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=requester_user_id,
        )
        if requester is None or requester.role != OrganizationMemberRole.OWNER:
            raise OrganizationAccessDeniedError(
                f"User {requester_user_id} cannot invite in organization {organization_id}"
            )
