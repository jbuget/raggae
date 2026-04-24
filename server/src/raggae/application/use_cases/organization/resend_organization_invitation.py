import logging
from datetime import UTC, datetime, timedelta
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
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.application.interfaces.services.invitation_email_service import InvitationEmailService
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationInvitationInvalidError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

logger = logging.getLogger(__name__)


class ResendOrganizationInvitation:
    """Use Case: Resend organization invitation (owner only)."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        organization_invitation_repository: OrganizationInvitationRepository,
        user_repository: UserRepository,
        invitation_email_service: InvitationEmailService,
        invitation_ttl_days: int = 7,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._organization_invitation_repository = organization_invitation_repository
        self._user_repository = user_repository
        self._invitation_email_service = invitation_email_service
        self._invitation_ttl_days = invitation_ttl_days

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
                f"User {requester_user_id} cannot resend invitation in organization {organization_id}"
            )
        invitation = await self._organization_invitation_repository.find_by_id(invitation_id)
        if invitation is None or invitation.organization_id != organization_id:
            raise OrganizationInvitationInvalidError(
                f"Invitation {invitation_id} not found in organization {organization_id}"
            )
        now = datetime.now(UTC)
        renewed = invitation.renew(
            expires_at=now + timedelta(days=self._invitation_ttl_days),
            updated_at=now,
        )
        await self._organization_invitation_repository.save(renewed)

        inviter = await self._user_repository.find_by_id(renewed.invited_by_user_id)
        inviter_name = inviter.full_name if inviter is not None else str(renewed.invited_by_user_id)
        try:
            await self._invitation_email_service.send_invitation_email(
                to_email=renewed.email,
                organization_name=organization.name,
                inviter_name=inviter_name,
                invitation_token=renewed.token_hash,
                expires_at=renewed.expires_at,
            )
        except Exception:
            logger.warning(
                "resend_invitation_email_send_failed",
                extra={"invitation_id": str(renewed.id)},
                exc_info=True,
            )

        return OrganizationInvitationDTO.from_entity(renewed)
