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
from raggae.domain.entities.user import User
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
from raggae.infrastructure.database.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)


class TestOrganizationMemberUseCases:
    @pytest.fixture
    async def setup_data(
        self,
    ) -> tuple[
        InMemoryOrganizationRepository,
        InMemoryOrganizationMemberRepository,
        InMemoryUserRepository,
        Organization,
        OrganizationMember,
        OrganizationMember,
        OrganizationMember,
    ]:
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        user_repo = InMemoryUserRepository()
        now = datetime.now(UTC)
        owner_user_id = uuid4()
        maker_user_id = uuid4()
        user_user_id = uuid4()
        org = Organization(
            id=uuid4(),
            name="Acme",
            slug=None,
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
        await user_repo.save(
            User(
                id=owner_user_id,
                email="owner@example.com",
                hashed_password="x",
                full_name="John Owner",
                is_active=True,
                created_at=now,
            )
        )
        await user_repo.save(
            User(
                id=maker_user_id,
                email="maker@example.com",
                hashed_password="x",
                full_name="Jane Maker",
                is_active=True,
                created_at=now,
            )
        )
        await user_repo.save(
            User(
                id=user_user_id,
                email="user@example.com",
                hashed_password="x",
                full_name="Alex User",
                is_active=True,
                created_at=now,
            )
        )
        return org_repo, member_repo, user_repo, org, owner, maker, user

    async def test_list_members_requires_membership(self, setup_data) -> None:
        org_repo, member_repo, user_repo, org, owner, _, _ = setup_data
        use_case = ListOrganizationMembers(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            user_repository=user_repo,
        )

        members = await use_case.execute(organization_id=org.id, user_id=owner.user_id)
        assert len(members) == 3
        assert members[0].user_first_name is not None

        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=org.id, user_id=uuid4())

    async def test_update_member_role_owner_only_and_last_owner_guard(self, setup_data) -> None:
        org_repo, member_repo, _, org, owner, maker, _ = setup_data
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
        org_repo, member_repo, _, org, owner, _, user = setup_data
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
