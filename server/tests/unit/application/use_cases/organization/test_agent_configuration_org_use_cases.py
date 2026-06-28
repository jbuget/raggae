from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.organization.get_org_agent_configuration import (
    GetOrgAgentConfiguration,
)
from raggae.application.use_cases.organization.upsert_org_agent_configuration import (
    UpsertOrgAgentConfiguration,
)
from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    InvalidProjectRerankerBackendError,
    InvalidProjectRetrievalStrategyError,
)
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_agent_configuration_repository import (
    InMemoryAgentConfigurationRepository,
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


def _make_agent_config(owner_id, config_type=AgentConfigurationType.ORGA, **kwargs):
    return AgentConfiguration(
        id=uuid4(),
        owner_id=owner_id,
        owner_type=config_type,
        **kwargs,
    )


class TestGetOrgAgentConfiguration:
    async def test_raises_not_found_when_org_missing(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = GetOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When / Then
        with pytest.raises(OrganizationNotFoundError):
            await use_case.execute(organization_id=uuid4(), user_id=uuid4())

    async def test_raises_access_denied_when_not_member(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        await org_repo.save(_make_org(org_id))
        use_case = GetOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=org_id, user_id=uuid4())

    async def test_returns_none_when_no_config_exists(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        use_case = GetOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When
        result = await use_case.execute(organization_id=org_id, user_id=user_id)

        # Then
        assert result is None

    async def test_returns_dto_when_config_exists(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        await config_repo.save(_make_agent_config(org_id, llm_backend="openai", llm_model="gpt-4.1"))
        use_case = GetOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When
        result = await use_case.execute(organization_id=org_id, user_id=user_id)

        # Then
        assert result is not None
        assert result.owner_id == org_id
        assert result.owner_type == AgentConfigurationType.ORGA
        assert result.llm_backend == "openai"
        assert result.llm_model == "gpt-4.1"

    async def test_member_with_maker_role_can_read_config(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id, role=OrganizationMemberRole.MAKER))
        use_case = GetOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When
        result = await use_case.execute(organization_id=org_id, user_id=user_id)

        # Then
        assert result is None


class TestUpsertOrgAgentConfiguration:
    async def test_raises_not_found_when_org_missing(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When / Then
        with pytest.raises(OrganizationNotFoundError):
            await use_case.execute(organization_id=uuid4(), user_id=uuid4())

    async def test_raises_access_denied_when_not_member(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        await org_repo.save(_make_org(org_id))
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=org_id, user_id=uuid4())

    async def test_raises_access_denied_when_member_is_not_owner(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id, role=OrganizationMemberRole.MAKER))
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=org_id, user_id=user_id)

    async def test_raises_invalid_embedding_backend_error(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectEmbeddingBackendError):
            await use_case.execute(
                organization_id=org_id, user_id=user_id, embedding_backend="unsupported_embed"
            )

    async def test_raises_invalid_llm_backend_error(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectLLMBackendError):
            await use_case.execute(organization_id=org_id, user_id=user_id, llm_backend="unsupported_llm")

    async def test_raises_invalid_retrieval_strategy_error(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectRetrievalStrategyError):
            await use_case.execute(
                organization_id=org_id, user_id=user_id, retrieval_strategy="unsupported_strategy"
            )

    async def test_raises_invalid_reranker_backend_error(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectRerankerBackendError):
            await use_case.execute(
                organization_id=org_id, user_id=user_id, reranker_backend="unsupported_reranker"
            )

    async def test_creates_config_when_none_exists(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When
        result = await use_case.execute(
            organization_id=org_id,
            user_id=user_id,
            llm_backend="openai",
            llm_model="gpt-4.1",
        )

        # Then
        assert result.owner_id == org_id
        assert result.owner_type == AgentConfigurationType.ORGA
        assert result.llm_backend == "openai"
        assert result.llm_model == "gpt-4.1"
        saved = await config_repo.find_by_owner(org_id, AgentConfigurationType.ORGA)
        assert saved is not None
        assert saved.llm_backend == "openai"

    async def test_updates_config_and_preserves_id_when_config_already_exists(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        existing_config = _make_agent_config(org_id, llm_backend="ollama")
        await config_repo.save(existing_config)
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When
        result = await use_case.execute(
            organization_id=org_id,
            user_id=user_id,
            llm_backend="openai",
        )

        # Then
        assert result.llm_backend == "openai"
        saved = await config_repo.find_by_owner(org_id, AgentConfigurationType.ORGA)
        assert saved is not None
        assert saved.id == existing_config.id
        assert saved.llm_backend == "openai"

    async def test_saves_with_orga_type(self) -> None:
        # Given
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        org_id = uuid4()
        user_id = uuid4()
        await org_repo.save(_make_org(org_id))
        await member_repo.save(_make_member(org_id, user_id))
        use_case = UpsertOrgAgentConfiguration(org_repo, member_repo, config_repo)

        # When
        result = await use_case.execute(organization_id=org_id, user_id=user_id)

        # Then
        assert result.owner_type == AgentConfigurationType.ORGA
        saved = await config_repo.find_by_owner(org_id, AgentConfigurationType.ORGA)
        assert saved is not None
        assert saved.owner_type == AgentConfigurationType.ORGA
