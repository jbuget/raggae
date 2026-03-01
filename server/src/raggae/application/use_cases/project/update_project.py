from dataclasses import replace
from uuid import UUID

from raggae.application.constants import (
    ALLOWED_EMBEDDING_MODELS,
    ALLOWED_LLM_MODELS,
    MAX_PROJECT_CHAT_HISTORY_MAX_CHARS,
    MAX_PROJECT_CHAT_HISTORY_WINDOW_SIZE,
    MAX_PROJECT_RERANKER_CANDIDATE_MULTIPLIER,
    MAX_PROJECT_RETRIEVAL_MIN_SCORE,
    MAX_PROJECT_RETRIEVAL_TOP_K,
    MAX_PROJECT_SYSTEM_PROMPT_LENGTH,
    MIN_PROJECT_CHAT_HISTORY_MAX_CHARS,
    MIN_PROJECT_CHAT_HISTORY_WINDOW_SIZE,
    MIN_PROJECT_RERANKER_CANDIDATE_MULTIPLIER,
    MIN_PROJECT_RETRIEVAL_MIN_SCORE,
    MIN_PROJECT_RETRIEVAL_TOP_K,
)
from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
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
    InvalidProjectChatHistoryMaxCharsError,
    InvalidProjectChatHistoryWindowSizeError,
    InvalidProjectEmbeddingBackendError,
    InvalidProjectEmbeddingModelError,
    InvalidProjectLLMBackendError,
    InvalidProjectLLMModelError,
    InvalidProjectRerankerBackendError,
    InvalidProjectRerankerCandidateMultiplierError,
    InvalidProjectRetrievalMinScoreError,
    InvalidProjectRetrievalStrategyError,
    InvalidProjectRetrievalTopKError,
    ProjectAPIKeyNotOwnedError,
    ProjectNotFoundError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

_SUPPORTED_EMBEDDING_BACKENDS = {"openai", "gemini", "ollama", "inmemory"}
_SUPPORTED_LLM_BACKENDS = {"openai", "gemini", "anthropic", "ollama", "inmemory"}
_SUPPORTED_RETRIEVAL_STRATEGIES = {"vector", "fulltext", "hybrid"}
_SUPPORTED_RERANKER_BACKENDS = {"none", "cross_encoder", "inmemory", "mmr"}


class UpdateProject:
    """Use Case: Update a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        organization_member_repository: OrganizationMemberRepository | None = None,
        provider_credential_repository: ProviderCredentialRepository | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._organization_member_repository = organization_member_repository
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
        retrieval_strategy: str | None = None,
        retrieval_top_k: int | None = None,
        retrieval_min_score: float | None = None,
        chat_history_window_size: int | None = None,
        chat_history_max_chars: int | None = None,
        reranking_enabled: bool | None = None,
        reranker_backend: str | None = None,
        reranker_model: str | None = None,
        reranker_candidate_multiplier: int | None = None,
    ) -> ProjectDTO:
        if len(system_prompt) > MAX_PROJECT_SYSTEM_PROMPT_LENGTH:
            raise ProjectSystemPromptTooLongError(
                f"System prompt exceeds {MAX_PROJECT_SYSTEM_PROMPT_LENGTH} characters"
            )
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        if project.user_id != user_id:
            if project.organization_id is None or self._organization_member_repository is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
            member = await self._organization_member_repository.find_by_organization_and_user(
                organization_id=project.organization_id,
                user_id=user_id,
            )
            if member is None or member.role not in {
                OrganizationMemberRole.OWNER,
                OrganizationMemberRole.MAKER,
            }:
                raise ProjectNotFoundError(f"Project {project_id} not found")
        if embedding_backend is not None and embedding_backend not in _SUPPORTED_EMBEDDING_BACKENDS:
            raise InvalidProjectEmbeddingBackendError(
                f"Unsupported embedding backend: {embedding_backend}"
            )
        if llm_backend is not None and llm_backend not in _SUPPORTED_LLM_BACKENDS:
            raise InvalidProjectLLMBackendError(f"Unsupported llm backend: {llm_backend}")
        if llm_model is not None and llm_model.strip() != "":
            effective_llm_backend = llm_backend if llm_backend is not None else project.llm_backend
            allowed_llm_models = ALLOWED_LLM_MODELS.get(effective_llm_backend or "")
            if allowed_llm_models is not None and llm_model.strip() not in allowed_llm_models:
                raise InvalidProjectLLMModelError(f"Unsupported llm model: {llm_model}")
        if embedding_model is not None and embedding_model.strip() != "":
            effective_embedding_backend = (
                embedding_backend if embedding_backend is not None else project.embedding_backend
            )
            allowed_embedding_models = ALLOWED_EMBEDDING_MODELS.get(
                effective_embedding_backend or ""
            )
            if (
                allowed_embedding_models is not None
                and embedding_model.strip() not in allowed_embedding_models
            ):
                raise InvalidProjectEmbeddingModelError(
                    f"Unsupported embedding model: {embedding_model}"
                )
        if (
            retrieval_strategy is not None
            and retrieval_strategy not in _SUPPORTED_RETRIEVAL_STRATEGIES
        ):
            raise InvalidProjectRetrievalStrategyError(
                f"Unsupported retrieval strategy: {retrieval_strategy}"
            )
        if retrieval_top_k is not None and not (
            MIN_PROJECT_RETRIEVAL_TOP_K <= retrieval_top_k <= MAX_PROJECT_RETRIEVAL_TOP_K
        ):
            raise InvalidProjectRetrievalTopKError(
                f"retrieval_top_k must be between {MIN_PROJECT_RETRIEVAL_TOP_K} "
                f"and {MAX_PROJECT_RETRIEVAL_TOP_K}"
            )
        if retrieval_min_score is not None and not (
            MIN_PROJECT_RETRIEVAL_MIN_SCORE
            <= retrieval_min_score
            <= MAX_PROJECT_RETRIEVAL_MIN_SCORE
        ):
            raise InvalidProjectRetrievalMinScoreError(
                f"retrieval_min_score must be between {MIN_PROJECT_RETRIEVAL_MIN_SCORE} "
                f"and {MAX_PROJECT_RETRIEVAL_MIN_SCORE}"
            )
        if chat_history_window_size is not None and not (
            MIN_PROJECT_CHAT_HISTORY_WINDOW_SIZE
            <= chat_history_window_size
            <= MAX_PROJECT_CHAT_HISTORY_WINDOW_SIZE
        ):
            raise InvalidProjectChatHistoryWindowSizeError(
                f"chat_history_window_size must be between "
                f"{MIN_PROJECT_CHAT_HISTORY_WINDOW_SIZE} and "
                f"{MAX_PROJECT_CHAT_HISTORY_WINDOW_SIZE}"
            )
        if chat_history_max_chars is not None and not (
            MIN_PROJECT_CHAT_HISTORY_MAX_CHARS
            <= chat_history_max_chars
            <= MAX_PROJECT_CHAT_HISTORY_MAX_CHARS
        ):
            raise InvalidProjectChatHistoryMaxCharsError(
                f"chat_history_max_chars must be between "
                f"{MIN_PROJECT_CHAT_HISTORY_MAX_CHARS} and "
                f"{MAX_PROJECT_CHAT_HISTORY_MAX_CHARS}"
            )
        if reranker_backend is not None and reranker_backend not in _SUPPORTED_RERANKER_BACKENDS:
            raise InvalidProjectRerankerBackendError(
                f"Unsupported reranker backend: {reranker_backend}"
            )
        if reranker_candidate_multiplier is not None and not (
            MIN_PROJECT_RERANKER_CANDIDATE_MULTIPLIER
            <= reranker_candidate_multiplier
            <= MAX_PROJECT_RERANKER_CANDIDATE_MULTIPLIER
        ):
            raise InvalidProjectRerankerCandidateMultiplierError(
                f"reranker_candidate_multiplier must be between "
                f"{MIN_PROJECT_RERANKER_CANDIDATE_MULTIPLIER} and "
                f"{MAX_PROJECT_RERANKER_CANDIDATE_MULTIPLIER}"
            )
        resolved_embedding_api_key = await self._resolve_api_key_from_credential_id(
            user_id=user_id,
            backend=(
                embedding_backend if embedding_backend is not None else project.embedding_backend
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
                embedding_backend if embedding_backend is not None else project.embedding_backend
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
        next_reranker_backend = (
            project.reranker_backend if reranker_backend is None else reranker_backend
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
            retrieval_strategy=(
                project.retrieval_strategy if retrieval_strategy is None else retrieval_strategy
            ),
            retrieval_top_k=project.retrieval_top_k if retrieval_top_k is None else retrieval_top_k,
            retrieval_min_score=(
                project.retrieval_min_score if retrieval_min_score is None else retrieval_min_score
            ),
            chat_history_window_size=(
                project.chat_history_window_size
                if chat_history_window_size is None
                else chat_history_window_size
            ),
            chat_history_max_chars=(
                project.chat_history_max_chars
                if chat_history_max_chars is None
                else chat_history_max_chars
            ),
            reranking_enabled=(
                project.reranking_enabled if reranking_enabled is None else reranking_enabled
            ),
            reranker_backend=next_reranker_backend,
            reranker_model=project.reranker_model if reranker_model is None else reranker_model,
            reranker_candidate_multiplier=(
                project.reranker_candidate_multiplier
                if reranker_candidate_multiplier is None
                else reranker_candidate_multiplier
            ),
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
                f"{config_type}_backend is required when "
                f"{config_type}_api_key_credential_id is provided"
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
