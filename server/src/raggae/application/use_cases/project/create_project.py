from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.constants import MAX_PROJECT_SYSTEM_PROMPT_LENGTH
from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)
from raggae.application.interfaces.repositories.provider_credential_repository import (
    ProviderCredentialRepository,
)
from raggae.application.interfaces.services.provider_api_key_crypto_service import (
    ProviderApiKeyCryptoService,
)
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    ProjectAPIKeyNotOwnedError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.model_provider import ModelProvider

_SUPPORTED_EMBEDDING_BACKENDS = {"openai", "gemini", "ollama", "inmemory"}
_SUPPORTED_LLM_BACKENDS = {"openai", "gemini", "anthropic", "ollama", "inmemory"}


class CreateProject:
    """Use Case: Create a new project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        provider_credential_repository: ProviderCredentialRepository | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._provider_credential_repository = provider_credential_repository
        self._provider_api_key_crypto_service: ProviderApiKeyCryptoService | None = None

    def with_crypto_service(
        self,
        provider_api_key_crypto_service: ProviderApiKeyCryptoService,
    ) -> "CreateProject":
        self._provider_api_key_crypto_service = provider_api_key_crypto_service
        return self

    async def execute(
        self,
        user_id: UUID,
        name: str,
        description: str,
        system_prompt: str,
        chunking_strategy: ChunkingStrategy | None = None,
        parent_child_chunking: bool | None = None,
        embedding_backend: str | None = None,
        embedding_model: str | None = None,
        embedding_api_key: str | None = None,
        llm_backend: str | None = None,
        llm_model: str | None = None,
        llm_api_key: str | None = None,
    ) -> ProjectDTO:
        if len(system_prompt) > MAX_PROJECT_SYSTEM_PROMPT_LENGTH:
            raise ProjectSystemPromptTooLongError(
                f"System prompt exceeds {MAX_PROJECT_SYSTEM_PROMPT_LENGTH} characters"
            )
        if embedding_backend is not None and embedding_backend not in _SUPPORTED_EMBEDDING_BACKENDS:
            raise InvalidProjectEmbeddingBackendError(
                f"Unsupported embedding backend: {embedding_backend}"
            )
        if llm_backend is not None and llm_backend not in _SUPPORTED_LLM_BACKENDS:
            raise InvalidProjectLLMBackendError(f"Unsupported llm backend: {llm_backend}")
        await self._validate_api_key_belongs_to_user(
            user_id=user_id,
            backend=embedding_backend,
            api_key=embedding_api_key,
            config_type="embedding",
        )
        await self._validate_api_key_belongs_to_user(
            user_id=user_id,
            backend=llm_backend,
            api_key=llm_api_key,
            config_type="llm",
        )
        encrypted_embedding_api_key = self._encrypt_api_key_if_provided(embedding_api_key)
        encrypted_llm_api_key = self._encrypt_api_key_if_provided(llm_api_key)
        project = Project(
            id=uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            is_published=False,
            created_at=datetime.now(UTC),
            chunking_strategy=chunking_strategy or ChunkingStrategy.AUTO,
            parent_child_chunking=parent_child_chunking or False,
            embedding_backend=embedding_backend,
            embedding_model=embedding_model,
            embedding_api_key_encrypted=encrypted_embedding_api_key,
            llm_backend=llm_backend,
            llm_model=llm_model,
            llm_api_key_encrypted=encrypted_llm_api_key,
        )

        await self._project_repository.save(project)

        return ProjectDTO.from_entity(project)

    def _encrypt_api_key_if_provided(self, api_key: str | None) -> str | None:
        if api_key is None or api_key.strip() == "":
            return None
        if self._provider_api_key_crypto_service is None:
            return api_key
        return self._provider_api_key_crypto_service.encrypt(api_key.strip())

    async def _validate_api_key_belongs_to_user(
        self,
        user_id: UUID,
        backend: str | None,
        api_key: str | None,
        config_type: str,
    ) -> None:
        if api_key is None or api_key.strip() == "":
            return
        if backend is None:
            raise ProjectAPIKeyNotOwnedError(
                f"{config_type}_backend is required when {config_type}_api_key is provided"
            )
        if backend not in {"openai", "gemini", "anthropic"}:
            raise ProjectAPIKeyNotOwnedError(
                f"{config_type}_api_key cannot be used with backend '{backend}'"
            )
        if self._provider_credential_repository is None:
            raise ProjectAPIKeyNotOwnedError("Provider credential repository is not configured")
        if self._provider_api_key_crypto_service is None:
            raise ProjectAPIKeyNotOwnedError("Provider crypto service is not configured")

        fingerprint = self._provider_api_key_crypto_service.fingerprint(api_key.strip())
        credentials = await self._provider_credential_repository.list_by_user_id_and_provider(
            user_id=user_id,
            provider=ModelProvider(backend),
        )
        if not any(credential.key_fingerprint == fingerprint for credential in credentials):
            raise ProjectAPIKeyNotOwnedError(
                f"{config_type}_api_key is not registered for this user and backend"
            )
