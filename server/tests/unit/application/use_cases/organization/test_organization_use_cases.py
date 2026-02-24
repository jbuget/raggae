from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.organization.create_organization import CreateOrganization
from raggae.application.use_cases.organization.delete_organization import DeleteOrganization
from raggae.application.use_cases.organization.get_organization import GetOrganization
from raggae.application.use_cases.organization.list_organizations import ListOrganizations
from raggae.application.use_cases.organization.update_organization import UpdateOrganization
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_organization_member_repository import (
    InMemoryOrganizationMemberRepository,
)
from raggae.infrastructure.database.repositories.in_memory_organization_repository import (
    InMemoryOrganizationRepository,
)


class TestOrganizationUseCases:
    @pytest.fixture
    def repositories(self) -> tuple[
        InMemoryOrganizationRepository, InMemoryOrganizationMemberRepository
    ]:
        return InMemoryOrganizationRepository(), InMemoryOrganizationMemberRepository()

    async def test_create_organization_bootstraps_owner(
        self,
        repositories: tuple[InMemoryOrganizationRepository, InMemoryOrganizationMemberRepository],
    ) -> None:
        org_repo, member_repo = repositories
        user_id = uuid4()
        use_case = CreateOrganization(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )

        created = await use_case.execute(user_id=user_id, name="Acme")

        members = await member_repo.find_by_organization_id(created.id)
        assert len(members) == 1
        assert members[0].user_id == user_id
        assert members[0].role == OrganizationMemberRole.OWNER
        assert created.slug is not None
        assert len(created.slug.split("-")) == 2

    async def test_create_organization_keeps_provided_slug(
        self,
        repositories: tuple[InMemoryOrganizationRepository, InMemoryOrganizationMemberRepository],
    ) -> None:
        org_repo, member_repo = repositories
        user_id = uuid4()
        use_case = CreateOrganization(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )

        created = await use_case.execute(user_id=user_id, name="Acme", slug="acme-team")

        assert created.slug == "acme-team"

    async def test_create_organization_generates_another_slug_on_collision(
        self,
        repositories: tuple[InMemoryOrganizationRepository, InMemoryOrganizationMemberRepository],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        org_repo, member_repo = repositories
        user_id = uuid4()
        now = datetime.now(UTC)
        existing = Organization(
            id=uuid4(),
            name="Existing",
            slug="agile-atelier",
            description=None,
            logo_url=None,
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        await org_repo.save(existing)

        choices = iter(["agile", "atelier", "brave", "bastion"])

        def fake_choice(_: list[str]) -> str:
            return next(choices)

        monkeypatch.setattr(
            "raggae.application.use_cases.organization.create_organization.random.choice",
            fake_choice,
        )

        use_case = CreateOrganization(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )

        created = await use_case.execute(user_id=uuid4(), name="Acme")

        assert created.slug is not None
        assert created.slug != "agile-atelier"

    async def test_get_and_list_organizations(
        self,
        repositories: tuple[InMemoryOrganizationRepository, InMemoryOrganizationMemberRepository],
    ) -> None:
        org_repo, member_repo = repositories
        user_id = uuid4()
        now = datetime.now(UTC)
        organization = Organization(
            id=uuid4(),
            name="Acme",
            slug=None,
            description=None,
            logo_url=None,
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        await org_repo.save(organization)
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=organization.id,
                user_id=user_id,
                role=OrganizationMemberRole.OWNER,
                joined_at=now,
            )
        )

        get_use_case = GetOrganization(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )
        list_use_case = ListOrganizations(organization_repository=org_repo)

        found = await get_use_case.execute(organization_id=organization.id, user_id=user_id)
        listed = await list_use_case.execute(user_id=user_id)

        assert found.id == organization.id
        assert len(listed) == 1

    async def test_update_organization_owner_only(
        self,
        repositories: tuple[InMemoryOrganizationRepository, InMemoryOrganizationMemberRepository],
    ) -> None:
        org_repo, member_repo = repositories
        owner_id = uuid4()
        other_user_id = uuid4()
        now = datetime.now(UTC)
        organization = Organization(
            id=uuid4(),
            name="Acme",
            slug=None,
            description=None,
            logo_url=None,
            created_by_user_id=owner_id,
            created_at=now,
            updated_at=now,
        )
        await org_repo.save(organization)
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=organization.id,
                user_id=owner_id,
                role=OrganizationMemberRole.OWNER,
                joined_at=now,
            )
        )

        use_case = UpdateOrganization(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )

        updated = await use_case.execute(
            organization_id=organization.id,
            user_id=owner_id,
            name="Acme Updated",
            slug="acme-updated",
            description="desc",
            logo_url=None,
        )
        assert updated.name == "Acme Updated"
        assert updated.slug == "acme-updated"

        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                organization_id=organization.id,
                user_id=other_user_id,
                name="Denied",
                slug=None,
                description=None,
                logo_url=None,
            )

    async def test_delete_organization_owner_only(
        self,
        repositories: tuple[InMemoryOrganizationRepository, InMemoryOrganizationMemberRepository],
    ) -> None:
        org_repo, member_repo = repositories
        owner_id = uuid4()
        now = datetime.now(UTC)
        organization = Organization(
            id=uuid4(),
            name="Acme",
            slug=None,
            description=None,
            logo_url=None,
            created_by_user_id=owner_id,
            created_at=now,
            updated_at=now,
        )
        await org_repo.save(organization)
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=organization.id,
                user_id=owner_id,
                role=OrganizationMemberRole.OWNER,
                joined_at=now,
            )
        )

        use_case = DeleteOrganization(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )
        await use_case.execute(organization_id=organization.id, user_id=owner_id)
        assert await org_repo.find_by_id(organization.id) is None

    async def test_get_organization_errors(
        self,
        repositories: tuple[InMemoryOrganizationRepository, InMemoryOrganizationMemberRepository],
    ) -> None:
        org_repo, member_repo = repositories
        use_case = GetOrganization(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
        )
        with pytest.raises(OrganizationNotFoundError):
            await use_case.execute(organization_id=uuid4(), user_id=uuid4())
