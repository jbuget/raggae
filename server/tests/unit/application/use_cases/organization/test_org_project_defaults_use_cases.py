from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.organization.get_org_project_defaults import (
    GetOrganizationProjectDefaults,
)
from raggae.application.use_cases.organization.upsert_org_project_defaults import (
    UpsertOrganizationProjectDefaults,
)
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.organization_project_defaults import OrganizationProjectDefaults
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_org_project_defaults_repository import (
    InMemoryOrgProjectDefaultsRepository,
)
from raggae.infrastructure.database.repositories.in_memory_organization_member_repository import (
    InMemoryOrganizationMemberRepository,
)
from raggae.infrastructure.database.repositories.in_memory_organization_repository import (
    InMemoryOrganizationRepository,
)


def _make_org(org_id=None):
    return Organization(
        id=org_id or uuid4(),
        name="Test Org",
        slug=None,
        description=None,
        logo_url=None,
        created_by_user_id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _make_member(org_id, user_id, role=OrganizationMemberRole.OWNER):
    return OrganizationMember(
        id=uuid4(),
        organization_id=org_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.now(UTC),
    )


class TestGetOrganizationProjectDefaults:
    @pytest.fixture
    def repos(self):
        return (
            InMemoryOrganizationRepository(),
            InMemoryOrganizationMemberRepository(),
            InMemoryOrgProjectDefaultsRepository(),
        )

    async def test_returns_none_when_no_defaults_configured(self, repos) -> None:
        # Given
        org_repo, member_repo, defaults_repo = repos
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        use_case = GetOrganizationProjectDefaults(org_repo, member_repo, defaults_repo)

        # When
        result = await use_case.execute(organization_id=org_id, user_id=user_id)

        # Then
        assert result is None

    async def test_returns_dto_when_defaults_configured(self, repos) -> None:
        # Given
        org_repo, member_repo, defaults_repo = repos
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        await defaults_repo.save(OrganizationProjectDefaults(organization_id=org_id, llm_backend="openai"))
        use_case = GetOrganizationProjectDefaults(org_repo, member_repo, defaults_repo)

        # When
        result = await use_case.execute(organization_id=org_id, user_id=user_id)

        # Then
        assert result is not None
        assert result.organization_id == org_id
        assert result.llm_backend == "openai"

    async def test_raises_not_found_when_org_missing(self, repos) -> None:
        # Given
        org_repo, member_repo, defaults_repo = repos
        use_case = GetOrganizationProjectDefaults(org_repo, member_repo, defaults_repo)

        # When / Then
        with pytest.raises(OrganizationNotFoundError):
            await use_case.execute(organization_id=uuid4(), user_id=uuid4())

    async def test_raises_access_denied_when_not_member(self, repos) -> None:
        # Given
        org_repo, member_repo, defaults_repo = repos
        org_id = uuid4()
        await org_repo.save(_make_org(org_id))
        use_case = GetOrganizationProjectDefaults(org_repo, member_repo, defaults_repo)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=org_id, user_id=uuid4())

    async def test_maker_can_read_defaults(self, repos) -> None:
        # Given
        org_repo, member_repo, defaults_repo = repos
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id, role=OrganizationMemberRole.MAKER))
        use_case = GetOrganizationProjectDefaults(org_repo, member_repo, defaults_repo)

        # When
        result = await use_case.execute(organization_id=org_id, user_id=user_id)

        # Then
        assert result is None


class TestUpsertOrganizationProjectDefaults:
    @pytest.fixture
    def repos(self):
        return (
            InMemoryOrganizationRepository(),
            InMemoryOrganizationMemberRepository(),
            InMemoryOrgProjectDefaultsRepository(),
        )

    async def test_owner_can_upsert_defaults(self, repos) -> None:
        # Given
        org_repo, member_repo, defaults_repo = repos
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        use_case = UpsertOrganizationProjectDefaults(org_repo, member_repo, defaults_repo)

        # When
        result = await use_case.execute(
            organization_id=org_id,
            user_id=user_id,
            llm_backend="openai",
            llm_model="gpt-4o",
        )

        # Then
        assert result.organization_id == org_id
        assert result.llm_backend == "openai"
        assert result.llm_model == "gpt-4o"

    async def test_upsert_replaces_existing_defaults(self, repos) -> None:
        # Given
        org_repo, member_repo, defaults_repo = repos
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        await defaults_repo.save(OrganizationProjectDefaults(organization_id=org_id, llm_backend="ollama"))
        use_case = UpsertOrganizationProjectDefaults(org_repo, member_repo, defaults_repo)

        # When
        result = await use_case.execute(
            organization_id=org_id,
            user_id=user_id,
            llm_backend="openai",
        )

        # Then
        assert result.llm_backend == "openai"
        saved = await defaults_repo.find_by_organization_id(org_id)
        assert saved is not None
        assert saved.llm_backend == "openai"

    async def test_maker_cannot_upsert_defaults(self, repos) -> None:
        # Given
        org_repo, member_repo, defaults_repo = repos
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id, role=OrganizationMemberRole.MAKER))
        use_case = UpsertOrganizationProjectDefaults(org_repo, member_repo, defaults_repo)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=org_id, user_id=user_id)

    async def test_raises_not_found_when_org_missing(self, repos) -> None:
        # Given
        org_repo, member_repo, defaults_repo = repos
        use_case = UpsertOrganizationProjectDefaults(org_repo, member_repo, defaults_repo)

        # When / Then
        with pytest.raises(OrganizationNotFoundError):
            await use_case.execute(organization_id=uuid4(), user_id=uuid4())
