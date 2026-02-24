from datetime import UTC, datetime, timedelta
from uuid import uuid4

from raggae.domain.entities.organization_invitation import OrganizationInvitation
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class TestOrganizationInvitation:
    def test_with_status_returns_updated_copy(self) -> None:
        now = datetime.now(UTC)
        invitation = OrganizationInvitation(
            id=uuid4(),
            organization_id=uuid4(),
            email="user@example.com",
            role=OrganizationMemberRole.USER,
            status=OrganizationInvitationStatus.PENDING,
            invited_by_user_id=uuid4(),
            token_hash="hash",
            expires_at=now + timedelta(days=7),
            created_at=now,
            updated_at=now,
        )

        accepted = invitation.with_status(
            status=OrganizationInvitationStatus.ACCEPTED,
            updated_at=now + timedelta(minutes=1),
        )

        assert accepted.status == OrganizationInvitationStatus.ACCEPTED
        assert invitation.status == OrganizationInvitationStatus.PENDING

    def test_renew_sets_pending_and_new_expiry(self) -> None:
        now = datetime.now(UTC)
        invitation = OrganizationInvitation(
            id=uuid4(),
            organization_id=uuid4(),
            email="user@example.com",
            role=OrganizationMemberRole.MAKER,
            status=OrganizationInvitationStatus.EXPIRED,
            invited_by_user_id=uuid4(),
            token_hash="hash",
            expires_at=now - timedelta(days=1),
            created_at=now - timedelta(days=8),
            updated_at=now - timedelta(days=1),
        )

        renewed = invitation.renew(
            expires_at=now + timedelta(days=7),
            updated_at=now,
        )

        assert renewed.status == OrganizationInvitationStatus.PENDING
        assert renewed.expires_at > now
