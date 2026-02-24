from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.organization.leave_organization import LeaveOrganization
from raggae.application.use_cases.organization.list_organization_members import (
    ListOrganizationMembers,
)
from raggae.application.use_cases.organization.remove_organization_member import (
    RemoveOrganizationMember,
)
from raggae.application.use_cases.organization.update_organization_member_role import (
    UpdateOrganizationMemberRole,
)
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.exceptions.organization_exceptions import (
    LastOrganizationOwnerError,
    OrganizationAccessDeniedError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_organization_member_repository import (
    InMemoryOrganizationMemberRepository,
)
from raggae.infrastructure.database.repositories.in_memory_organization_repository import (
    InMemoryOrganizationRepository,
)


class TestOrganizationMemberUseCases:
    @pytest.fixture
    async def setup_data(
        self,
    ) -> tuple[
        InMemoryOrganizationRepository,
        InMemoryOrganizationMemberRepository,
        Organization,
        OrganizationMember,
        OrganizationMember,
        OrganizationMember,
    ]:
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        now = datetime.now(UTC)
        owner_user_id = uuid4()
        maker_user_id = uuid4()
        user_user_id = uuid4()
        org = Organization(
            id=uuid4(),
            name="Acme",
            description=None,
            logo_url=None,
            created_by_user_id=owner_user_id,
            created_at=now,
            updated_at=now,
        )
        owner = OrganizationMember(
            id=uuid4(),
            organization_id=org.id,
            user_id=owner_user_id,
            role=OrganizationMemberRole.OWNER,
            joined_at=now,
        )
        maker = OrganizationMember(
            id=uuid4(),
            organization_id=org.id,
            user_id=maker_user_id,
            role=OrganizationMemberRole.MAKER,
            joined_at=now,
        )
        user = OrganizationMember(
            id=uuid4(),
            organization_id=org.id,
            user_id=user_user_id,
            role=OrganizationMemberRole.USER,
            joined_at=now,
        )
        await org_repo.save(org)
        await member_repo.save(owner)
        await member_repo.save(maker)
        await member_repo.save(user)
        return org_repo, member_repo, org, owner, maker, user

    async def test_list_members_requires_membership(self, setup_data) -> None:
        org_repo, member_repo, org, owner, _, _ = setup_data
        use_case = ListOrganizationMembers(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )

        members = await use_case.execute(organization_id=org.id, user_id=owner.user_id)
        assert len(members) == 3

        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=org.id, user_id=uuid4())

    async def test_update_member_role_owner_only_and_last_owner_guard(self, setup_data) -> None:
        org_repo, member_repo, org, owner, maker, _ = setup_data
        use_case = UpdateOrganizationMemberRole(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )

        with pytest.raises(LastOrganizationOwnerError):
            await use_case.execute(
                organization_id=org.id,
                requester_user_id=owner.user_id,
                member_id=owner.id,
                role=OrganizationMemberRole.USER,
            )

        updated = await use_case.execute(
            organization_id=org.id,
            requester_user_id=owner.user_id,
            member_id=maker.id,
            role=OrganizationMemberRole.OWNER,
        )
        assert updated.role == OrganizationMemberRole.OWNER

    async def test_remove_member_and_leave_with_last_owner_guard(self, setup_data) -> None:
        org_repo, member_repo, org, owner, _, user = setup_data
        remove_use_case = RemoveOrganizationMember(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )
        leave_use_case = LeaveOrganization(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )

        await remove_use_case.execute(
            organization_id=org.id,
            requester_user_id=owner.user_id,
            member_id=user.id,
        )
        assert await member_repo.find_by_id(user.id) is None

        with pytest.raises(LastOrganizationOwnerError):
            await leave_use_case.execute(organization_id=org.id, user_id=owner.user_id)
