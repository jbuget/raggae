from uuid import UUID, uuid4

from raggae.application.interfaces.repositories.agent_configuration_repository import (
    AgentConfigurationRepository,
)
from raggae.application.interfaces.repositories.org_provider_credential_repository import (
    OrgProviderCredentialRepository,
)
from raggae.application.interfaces.repositories.provider_credential_repository import (
    ProviderCredentialRepository,
)
from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.entities.project import Project
from raggae.domain.services.config_extractor import ConfigExtractor
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.domain.value_objects.resolved_agent_configuration import ResolvedAgentConfiguration


class AgentConfigurationResolver:
    """Application service: resolves a project's effective AgentConfiguration and
    dereferences API key credentials.

    Centralises the cascade Project -> (Org or User) -> App via ConfigExtractor and
    the credential lookup across org and user credential repositories, so use cases
    do not duplicate this orchestration.
    """

    def __init__(
        self,
        agent_configuration_repository: AgentConfigurationRepository,
        org_provider_credential_repository: OrgProviderCredentialRepository | None = None,
        provider_credential_repository: ProviderCredentialRepository | None = None,
    ) -> None:
        self._agent_configuration_repository = agent_configuration_repository
        self._org_provider_credential_repository = org_provider_credential_repository
        self._provider_credential_repository = provider_credential_repository

    async def resolve(self, project: Project, user_id: UUID) -> ResolvedAgentConfiguration:
        project_config = await self._agent_configuration_repository.find_by_owner(
            project.id, AgentConfigurationType.PROJECT
        )
        base_config = project_config or AgentConfiguration(
            id=uuid4(), owner_id=project.id, owner_type=AgentConfigurationType.PROJECT
        )
        if project.organization_id is not None:
            parent_config = await self._agent_configuration_repository.find_by_owner(
                project.organization_id, AgentConfigurationType.ORGA
            )
        else:
            parent_config = await self._agent_configuration_repository.find_by_owner(
                user_id, AgentConfigurationType.USER
            )
        app_config = await self._agent_configuration_repository.find_app_defaults()
        return ConfigExtractor.resolve(base_config, parent_config, app_config)

    async def fetch_encrypted_api_key(
        self, credential_id: UUID | None, project: Project, user_id: UUID
    ) -> str | None:
        if credential_id is None:
            return None
        if project.organization_id is not None and self._org_provider_credential_repository is not None:
            org_creds = await self._org_provider_credential_repository.list_by_org_id(project.organization_id)
            org_cred = next((c for c in org_creds if c.id == credential_id), None)
            if org_cred is not None:
                return org_cred.encrypted_api_key
        if self._provider_credential_repository is not None:
            user_creds = await self._provider_credential_repository.list_by_user_id(user_id)
            user_cred = next((c for c in user_creds if c.id == credential_id), None)
            if user_cred is not None:
                return user_cred.encrypted_api_key
        return None
