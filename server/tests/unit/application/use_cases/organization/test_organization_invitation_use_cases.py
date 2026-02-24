from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from raggae.application.use_cases.organization.accept_organization_invitation import (
    AcceptOrganizationInvitation,
)
from raggae.application.use_cases.organization.invite_organization_member import (
    InviteOrganizationMember,
)
from raggae.application.use_cases.organization.list_organization_invitations import (
    ListOrganizationInvitations,
)
from raggae.application.use_cases.organization.resend_organization_invitation import (
    ResendOrganizationInvitation,
)
from raggae.application.use_cases.organization.revoke_organization_invitation import (
    RevokeOrganizationInvitation,
)
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_invitation import OrganizationInvitation
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationInvitationInvalidError,
)
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_organization_invitation_repository import (
    InMemoryOrganizationInvitationRepository,
)
from raggae.infrastructure.database.repositories.in_memory_organization_member_repository import (
    InMemoryOrganizationMemberRepository,
)
from raggae.infrastructure.database.repositories.in_memory_organization_repository import (
    InMemoryOrganizationRepository,
)


class TestOrganizationInvitationUseCases:
    @pytest.fixture
    async def setup_data(self):
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        invitation_repo = InMemoryOrganizationInvitationRepository()
        now = datetime.now(UTC)
        owner_id = uuid4()
        org = Organization(
            id=uuid4(),
            name="Acme",
            slug=None,
            description=None,
            logo_url=None,
            created_by_user_id=owner_id,
            created_at=now,
            updated_at=now,
        )
        owner = OrganizationMember(
            id=uuid4(),
            organization_id=org.id,
            user_id=owner_id,
            role=OrganizationMemberRole.OWNER,
            joined_at=now,
        )
        await org_repo.save(org)
        await member_repo.save(owner)
        return org_repo, member_repo, invitation_repo, org, owner

    async def test_invite_and_list_and_resend_and_revoke(self, setup_data) -> None:
        org_repo, member_repo, invitation_repo, org, owner = setup_data
        invite = InviteOrganizationMember(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            organization_invitation_repository=invitation_repo,
            invitation_ttl_days=7,
        )
        list_use_case = ListOrganizationInvitations(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            organization_invitation_repository=invitation_repo,
        )
        resend = ResendOrganizationInvitation(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            organization_invitation_repository=invitation_repo,
            invitation_ttl_days=7,
        )
        revoke = RevokeOrganizationInvitation(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            organization_invitation_repository=invitation_repo,
        )

        created = await invite.execute(
            organization_id=org.id,
            requester_user_id=owner.user_id,
            email="user@example.com",
            role=OrganizationMemberRole.MAKER,
        )
        listed = await list_use_case.execute(organization_id=org.id, requester_user_id=owner.user_id)
        renewed = await resend.execute(
            organization_id=org.id,
            requester_user_id=owner.user_id,
            invitation_id=created.id,
        )
        revoked = await revoke.execute(
            organization_id=org.id,
            requester_user_id=owner.user_id,
            invitation_id=created.id,
        )

        assert len(listed) == 1
        assert renewed.status == OrganizationInvitationStatus.PENDING
        assert revoked.status == OrganizationInvitationStatus.REVOKED

    async def test_accept_invitation(self, setup_data) -> None:
        org_repo, member_repo, invitation_repo, org, owner = setup_data
        now = datetime.now(UTC)
        invitation = OrganizationInvitation(
            id=uuid4(),
            organization_id=org.id,
            email="new@example.com",
            role=OrganizationMemberRole.USER,
            status=OrganizationInvitationStatus.PENDING,
            invited_by_user_id=owner.user_id,
            token_hash="token-hash",
            expires_at=now + timedelta(days=1),
            created_at=now,
            updated_at=now,
        )
        await invitation_repo.save(invitation)
        use_case = AcceptOrganizationInvitation(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            organization_invitation_repository=invitation_repo,
        )

        accepted_member = await use_case.execute(token_hash="token-hash", user_id=uuid4())
        saved_invitation = await invitation_repo.find_by_id(invitation.id)

        assert accepted_member.organization_id == org.id
        assert saved_invitation is not None
        assert saved_invitation.status == OrganizationInvitationStatus.ACCEPTED

    async def test_accept_expired_invitation_raises(self, setup_data) -> None:
        org_repo, member_repo, invitation_repo, org, owner = setup_data
        now = datetime.now(UTC)
        invitation = OrganizationInvitation(
            id=uuid4(),
            organization_id=org.id,
            email="new@example.com",
            role=OrganizationMemberRole.USER,
            status=OrganizationInvitationStatus.PENDING,
            invited_by_user_id=owner.user_id,
            token_hash="expired-token",
            expires_at=now - timedelta(minutes=1),
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        )
        await invitation_repo.save(invitation)
        use_case = AcceptOrganizationInvitation(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            organization_invitation_repository=invitation_repo,
        )

        with pytest.raises(OrganizationInvitationInvalidError):
            await use_case.execute(token_hash="expired-token", user_id=uuid4())
