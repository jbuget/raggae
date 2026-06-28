from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.services.agent_configuration_resolver import (
    AgentConfigurationResolver,
)
from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.entities.org_model_provider_credential import OrgModelProviderCredential
from raggae.domain.entities.project import Project
from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.domain.value_objects.model_provider import ModelProvider


def _make_project(*, organization_id=None) -> Project:
    return Project(
        id=uuid4(),
        user_id=uuid4(),
        name="P",
        description="",
        system_prompt="",
        is_published=False,
        created_at=datetime.now(UTC),
        organization_id=organization_id,
    )


class TestAgentConfigurationResolverResolve:
    async def test_returns_project_values_when_present(self) -> None:
        project = _make_project()
        user_id = uuid4()
        agent_config_repo = AsyncMock()

        async def find_by_owner(owner_id, owner_type):
            if owner_id == project.id and owner_type == AgentConfigurationType.PROJECT:
                return AgentConfiguration(
                    id=uuid4(),
                    owner_id=project.id,
                    owner_type=AgentConfigurationType.PROJECT,
                    llm_backend="openai",
                    llm_model="gpt-4o",
                )
            return None

        agent_config_repo.find_by_owner.side_effect = find_by_owner
        agent_config_repo.find_app_defaults.return_value = None
        resolver = AgentConfigurationResolver(agent_configuration_repository=agent_config_repo)

        resolved = await resolver.resolve(project=project, user_id=user_id)

        assert resolved.llm_backend == "openai"
        assert resolved.llm_model == "gpt-4o"

    async def test_cascades_to_org_when_project_value_missing(self) -> None:
        organization_id = uuid4()
        project = _make_project(organization_id=organization_id)
        agent_config_repo = AsyncMock()

        async def find_by_owner(owner_id, owner_type):
            if owner_id == organization_id and owner_type == AgentConfigurationType.ORGA:
                return AgentConfiguration(
                    id=uuid4(),
                    owner_id=organization_id,
                    owner_type=AgentConfigurationType.ORGA,
                    llm_backend="gemini",
                    llm_model="gemini-1.5-flash",
                )
            return None

        agent_config_repo.find_by_owner.side_effect = find_by_owner
        agent_config_repo.find_app_defaults.return_value = None
        resolver = AgentConfigurationResolver(agent_configuration_repository=agent_config_repo)

        resolved = await resolver.resolve(project=project, user_id=uuid4())

        assert resolved.llm_backend == "gemini"
        assert resolved.llm_model == "gemini-1.5-flash"

    async def test_cascades_to_user_when_project_has_no_organization(self) -> None:
        project = _make_project(organization_id=None)
        user_id = uuid4()
        agent_config_repo = AsyncMock()

        async def find_by_owner(owner_id, owner_type):
            if owner_id == user_id and owner_type == AgentConfigurationType.USER:
                return AgentConfiguration(
                    id=uuid4(),
                    owner_id=user_id,
                    owner_type=AgentConfigurationType.USER,
                    llm_backend="ollama",
                    llm_model="llama3.1",
                )
            return None

        agent_config_repo.find_by_owner.side_effect = find_by_owner
        agent_config_repo.find_app_defaults.return_value = None
        resolver = AgentConfigurationResolver(agent_configuration_repository=agent_config_repo)

        resolved = await resolver.resolve(project=project, user_id=user_id)

        assert resolved.llm_backend == "ollama"
        assert resolved.llm_model == "llama3.1"

    async def test_falls_back_to_app_defaults_when_no_project_or_parent(self) -> None:
        project = _make_project()
        app_defaults = AgentConfiguration(
            id=uuid4(),
            owner_id=uuid4(),
            owner_type=AgentConfigurationType.APP,
            llm_backend="openai",
            llm_model="gpt-4o-mini",
        )
        agent_config_repo = AsyncMock()
        agent_config_repo.find_by_owner.return_value = None
        agent_config_repo.find_app_defaults.return_value = app_defaults
        resolver = AgentConfigurationResolver(agent_configuration_repository=agent_config_repo)

        resolved = await resolver.resolve(project=project, user_id=uuid4())

        assert resolved.llm_backend == "openai"
        assert resolved.llm_model == "gpt-4o-mini"

    async def test_returns_resolved_with_none_values_when_nothing_configured(self) -> None:
        project = _make_project()
        agent_config_repo = AsyncMock()
        agent_config_repo.find_by_owner.return_value = None
        agent_config_repo.find_app_defaults.return_value = None
        resolver = AgentConfigurationResolver(agent_configuration_repository=agent_config_repo)

        resolved = await resolver.resolve(project=project, user_id=uuid4())

        assert resolved.llm_backend is None
        assert resolved.llm_model is None
        assert resolved.embedding_backend is None


class TestAgentConfigurationResolverFetchEncryptedApiKey:
    async def test_returns_none_when_credential_id_is_none(self) -> None:
        resolver = AgentConfigurationResolver(agent_configuration_repository=AsyncMock())

        result = await resolver.fetch_encrypted_api_key(
            credential_id=None, project=_make_project(), user_id=uuid4()
        )

        assert result is None

    async def test_prefers_org_credential_when_project_has_organization(self) -> None:
        organization_id = uuid4()
        project = _make_project(organization_id=organization_id)
        credential_id = uuid4()
        org_credential = OrgModelProviderCredential(
            id=credential_id,
            organization_id=organization_id,
            provider=ModelProvider("openai"),
            encrypted_api_key="org-secret",
            key_fingerprint="fp",
            key_suffix="abcd",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        org_credential_repo = AsyncMock()
        org_credential_repo.list_by_org_id.return_value = [org_credential]
        user_credential_repo = AsyncMock()
        resolver = AgentConfigurationResolver(
            agent_configuration_repository=AsyncMock(),
            org_provider_credential_repository=org_credential_repo,
            provider_credential_repository=user_credential_repo,
        )

        result = await resolver.fetch_encrypted_api_key(
            credential_id=credential_id, project=project, user_id=uuid4()
        )

        assert result == "org-secret"
        user_credential_repo.list_by_user_id.assert_not_awaited()

    async def test_falls_back_to_user_credential_when_org_lookup_misses(self) -> None:
        organization_id = uuid4()
        project = _make_project(organization_id=organization_id)
        credential_id = uuid4()
        user_id = uuid4()
        user_credential = UserModelProviderCredential(
            id=credential_id,
            user_id=user_id,
            provider=ModelProvider("openai"),
            encrypted_api_key="user-secret",
            key_fingerprint="fp",
            key_suffix="abcd",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        org_credential_repo = AsyncMock()
        org_credential_repo.list_by_org_id.return_value = []
        user_credential_repo = AsyncMock()
        user_credential_repo.list_by_user_id.return_value = [user_credential]
        resolver = AgentConfigurationResolver(
            agent_configuration_repository=AsyncMock(),
            org_provider_credential_repository=org_credential_repo,
            provider_credential_repository=user_credential_repo,
        )

        result = await resolver.fetch_encrypted_api_key(
            credential_id=credential_id, project=project, user_id=user_id
        )

        assert result == "user-secret"

    async def test_returns_none_when_credential_not_found_anywhere(self) -> None:
        project = _make_project(organization_id=uuid4())
        org_credential_repo = AsyncMock()
        org_credential_repo.list_by_org_id.return_value = []
        user_credential_repo = AsyncMock()
        user_credential_repo.list_by_user_id.return_value = []
        resolver = AgentConfigurationResolver(
            agent_configuration_repository=AsyncMock(),
            org_provider_credential_repository=org_credential_repo,
            provider_credential_repository=user_credential_repo,
        )

        result = await resolver.fetch_encrypted_api_key(
            credential_id=uuid4(), project=project, user_id=uuid4()
        )

        assert result is None


pytestmark = pytest.mark.asyncio
