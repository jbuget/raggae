from dataclasses import replace
from uuid import UUID

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
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    ProjectAPIKeyNotOwnedError,
    ProjectNotFoundError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.model_provider import ModelProvider

_SUPPORTED_EMBEDDING_BACKENDS = {"openai", "gemini", "ollama", "inmemory"}
_SUPPORTED_LLM_BACKENDS = {"openai", "gemini", "anthropic", "ollama", "inmemory"}


class UpdateProject:
    """Use Case: Update a project."""

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
    ) -> "UpdateProject":
        self._provider_api_key_crypto_service = provider_api_key_crypto_service
        return self

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        name: str,
        description: str,
        system_prompt: str,
        chunking_strategy: ChunkingStrategy | None = None,
        parent_child_chunking: bool | None = None,
        embedding_backend: str | None = None,
        embedding_model: str | None = None,
        embedding_api_key: str | None = None,
        embedding_api_key_credential_id: UUID | None = None,
        llm_backend: str | None = None,
        llm_model: str | None = None,
        llm_api_key: str | None = None,
        llm_api_key_credential_id: UUID | None = None,
    ) -> ProjectDTO:
        if len(system_prompt) > MAX_PROJECT_SYSTEM_PROMPT_LENGTH:
            raise ProjectSystemPromptTooLongError(
                f"System prompt exceeds {MAX_PROJECT_SYSTEM_PROMPT_LENGTH} characters"
            )
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        if embedding_backend is not None and embedding_backend not in _SUPPORTED_EMBEDDING_BACKENDS:
            raise InvalidProjectEmbeddingBackendError(
                f"Unsupported embedding backend: {embedding_backend}"
            )
        if llm_backend is not None and llm_backend not in _SUPPORTED_LLM_BACKENDS:
            raise InvalidProjectLLMBackendError(f"Unsupported llm backend: {llm_backend}")
        resolved_embedding_api_key = await self._resolve_api_key_from_credential_id(
            user_id=user_id,
            backend=(
                embedding_backend
                if embedding_backend is not None
                else project.embedding_backend
            ),
            api_key=embedding_api_key,
            api_key_credential_id=embedding_api_key_credential_id,
            config_type="embedding",
        )
        resolved_llm_api_key = await self._resolve_api_key_from_credential_id(
            user_id=user_id,
            backend=llm_backend if llm_backend is not None else project.llm_backend,
            api_key=llm_api_key,
            api_key_credential_id=llm_api_key_credential_id,
            config_type="llm",
        )
        await self._validate_api_key_belongs_to_user(
            user_id=user_id,
            backend=(
                embedding_backend
                if embedding_backend is not None
                else project.embedding_backend
            ),
            api_key=resolved_embedding_api_key,
            config_type="embedding",
        )
        await self._validate_api_key_belongs_to_user(
            user_id=user_id,
            backend=llm_backend if llm_backend is not None else project.llm_backend,
            api_key=resolved_llm_api_key,
            config_type="llm",
        )

        encrypted_embedding_api_key = self._resolve_encrypted_api_key(
            current_value=project.embedding_api_key_encrypted,
            provided_value=resolved_embedding_api_key,
        )
        encrypted_llm_api_key = self._resolve_encrypted_api_key(
            current_value=project.llm_api_key_encrypted,
            provided_value=resolved_llm_api_key,
        )
        next_embedding_backend = (
            project.embedding_backend if embedding_backend is None else embedding_backend
        )
        next_llm_backend = project.llm_backend if llm_backend is None else llm_backend
        next_embedding_api_key_credential_id = self._resolve_next_credential_id(
            current_value=project.embedding_api_key_credential_id,
            provided_credential_id=embedding_api_key_credential_id,
            provided_api_key=embedding_api_key,
            backend=next_embedding_backend,
        )
        next_llm_api_key_credential_id = self._resolve_next_credential_id(
            current_value=project.llm_api_key_credential_id,
            provided_credential_id=llm_api_key_credential_id,
            provided_api_key=llm_api_key,
            backend=next_llm_backend,
        )
        updated_project = replace(
            project,
            name=name,
            description=description,
            system_prompt=system_prompt,
            chunking_strategy=project.chunking_strategy
            if chunking_strategy is None
            else chunking_strategy,
            parent_child_chunking=project.parent_child_chunking
            if parent_child_chunking is None
            else parent_child_chunking,
            embedding_backend=next_embedding_backend,
            embedding_model=project.embedding_model if embedding_model is None else embedding_model,
            embedding_api_key_encrypted=encrypted_embedding_api_key,
            embedding_api_key_credential_id=next_embedding_api_key_credential_id,
            llm_backend=next_llm_backend,
            llm_model=project.llm_model if llm_model is None else llm_model,
            llm_api_key_encrypted=encrypted_llm_api_key,
            llm_api_key_credential_id=next_llm_api_key_credential_id,
        )
        await self._project_repository.save(updated_project)
        return ProjectDTO.from_entity(updated_project)

    def _resolve_encrypted_api_key(
        self,
        current_value: str | None,
        provided_value: str | None,
    ) -> str | None:
        if provided_value is None:
            return current_value
        if provided_value.strip() == "":
            return None
        if self._provider_api_key_crypto_service is None:
            return provided_value.strip()
        return self._provider_api_key_crypto_service.encrypt(provided_value.strip())

    async def _validate_api_key_belongs_to_user(
        self,
        user_id: UUID,
        backend: str | None,
        api_key: str | None,
        config_type: str,
    ) -> None:
        if api_key is None:
            return
        if api_key.strip() == "":
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

    async def _resolve_api_key_from_credential_id(
        self,
        user_id: UUID,
        backend: str | None,
        api_key: str | None,
        api_key_credential_id: UUID | None,
        config_type: str,
    ) -> str | None:
        if api_key_credential_id is None:
            return api_key
        if api_key is not None and api_key.strip() != "":
            raise ProjectAPIKeyNotOwnedError(
                f"{config_type}_api_key and {config_type}_api_key_credential_id cannot both be set"
            )
        if backend is None:
            raise ProjectAPIKeyNotOwnedError(
                f"{config_type}_backend is required when {config_type}_api_key_credential_id is provided"
            )
        if backend not in {"openai", "gemini", "anthropic"}:
            raise ProjectAPIKeyNotOwnedError(
                f"{config_type}_api_key_credential_id cannot be used with backend '{backend}'"
            )
        if self._provider_credential_repository is None:
            raise ProjectAPIKeyNotOwnedError("Provider credential repository is not configured")
        if self._provider_api_key_crypto_service is None:
            raise ProjectAPIKeyNotOwnedError("Provider crypto service is not configured")
        credentials = await self._provider_credential_repository.list_by_user_id_and_provider(
            user_id=user_id,
            provider=ModelProvider(backend),
        )
        matching = next((cred for cred in credentials if cred.id == api_key_credential_id), None)
        if matching is None:
            raise ProjectAPIKeyNotOwnedError(
                f"{config_type}_api_key_credential_id is not registered for this user and backend"
            )
        return self._provider_api_key_crypto_service.decrypt(matching.encrypted_api_key)

    def _resolve_next_credential_id(
        self,
        current_value: UUID | None,
        provided_credential_id: UUID | None,
        provided_api_key: str | None,
        backend: str | None,
    ) -> UUID | None:
        if backend not in {"openai", "gemini", "anthropic"}:
            return None
        if provided_credential_id is not None:
            return provided_credential_id
        if provided_api_key is None:
            return current_value
        return None
