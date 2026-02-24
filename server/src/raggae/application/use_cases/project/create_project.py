from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.constants import (
    DEFAULT_PROJECT_CHAT_HISTORY_MAX_CHARS,
    DEFAULT_PROJECT_CHAT_HISTORY_WINDOW_SIZE,
    DEFAULT_PROJECT_RETRIEVAL_MIN_SCORE,
    DEFAULT_PROJECT_RERANKER_CANDIDATE_MULTIPLIER,
    DEFAULT_PROJECT_RETRIEVAL_TOP_K,
    MAX_PROJECT_CHAT_HISTORY_MAX_CHARS,
    MAX_PROJECT_CHAT_HISTORY_WINDOW_SIZE,
    MAX_PROJECT_RETRIEVAL_MIN_SCORE,
    MAX_PROJECT_RERANKER_CANDIDATE_MULTIPLIER,
    MAX_PROJECT_RETRIEVAL_TOP_K,
    MAX_PROJECT_SYSTEM_PROMPT_LENGTH,
    MIN_PROJECT_CHAT_HISTORY_MAX_CHARS,
    MIN_PROJECT_CHAT_HISTORY_WINDOW_SIZE,
    MIN_PROJECT_RETRIEVAL_MIN_SCORE,
    MIN_PROJECT_RERANKER_CANDIDATE_MULTIPLIER,
    MIN_PROJECT_RETRIEVAL_TOP_K,
)
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
    InvalidProjectChatHistoryMaxCharsError,
    InvalidProjectChatHistoryWindowSizeError,
    InvalidProjectLLMBackendError,
    InvalidProjectRerankerBackendError,
    InvalidProjectRerankerCandidateMultiplierError,
    InvalidProjectRetrievalMinScoreError,
    InvalidProjectRetrievalStrategyError,
    InvalidProjectRetrievalTopKError,
    ProjectAPIKeyNotOwnedError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.model_provider import ModelProvider

_SUPPORTED_EMBEDDING_BACKENDS = {"openai", "gemini", "ollama", "inmemory"}
_SUPPORTED_LLM_BACKENDS = {"openai", "gemini", "anthropic", "ollama", "inmemory"}
_SUPPORTED_RETRIEVAL_STRATEGIES = {"vector", "fulltext", "hybrid"}
_SUPPORTED_RERANKER_BACKENDS = {"none", "cross_encoder", "inmemory"}


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
        if embedding_backend is not None and embedding_backend not in _SUPPORTED_EMBEDDING_BACKENDS:
            raise InvalidProjectEmbeddingBackendError(
                f"Unsupported embedding backend: {embedding_backend}"
            )
        if llm_backend is not None and llm_backend not in _SUPPORTED_LLM_BACKENDS:
            raise InvalidProjectLLMBackendError(f"Unsupported llm backend: {llm_backend}")
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
            backend=embedding_backend,
            api_key=embedding_api_key,
            api_key_credential_id=embedding_api_key_credential_id,
            config_type="embedding",
        )
        resolved_llm_api_key = await self._resolve_api_key_from_credential_id(
            user_id=user_id,
            backend=llm_backend,
            api_key=llm_api_key,
            api_key_credential_id=llm_api_key_credential_id,
            config_type="llm",
        )
        await self._validate_api_key_belongs_to_user(
            user_id=user_id,
            backend=embedding_backend,
            api_key=resolved_embedding_api_key,
            config_type="embedding",
        )
        await self._validate_api_key_belongs_to_user(
            user_id=user_id,
            backend=llm_backend,
            api_key=resolved_llm_api_key,
            config_type="llm",
        )
        encrypted_embedding_api_key = self._encrypt_api_key_if_provided(resolved_embedding_api_key)
        encrypted_llm_api_key = self._encrypt_api_key_if_provided(resolved_llm_api_key)
        effective_embedding_api_key_credential_id = (
            embedding_api_key_credential_id
            if embedding_api_key_credential_id is not None
            and resolved_embedding_api_key is not None
            else None
        )
        effective_llm_api_key_credential_id = (
            llm_api_key_credential_id
            if llm_api_key_credential_id is not None and resolved_llm_api_key is not None
            else None
        )
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
            embedding_api_key_credential_id=effective_embedding_api_key_credential_id,
            llm_backend=llm_backend,
            llm_model=llm_model,
            llm_api_key_encrypted=encrypted_llm_api_key,
            llm_api_key_credential_id=effective_llm_api_key_credential_id,
            retrieval_strategy=retrieval_strategy or "hybrid",
            retrieval_top_k=retrieval_top_k or DEFAULT_PROJECT_RETRIEVAL_TOP_K,
            retrieval_min_score=(
                retrieval_min_score
                if retrieval_min_score is not None
                else DEFAULT_PROJECT_RETRIEVAL_MIN_SCORE
            ),
            chat_history_window_size=(
                chat_history_window_size
                if chat_history_window_size is not None
                else DEFAULT_PROJECT_CHAT_HISTORY_WINDOW_SIZE
            ),
            chat_history_max_chars=(
                chat_history_max_chars
                if chat_history_max_chars is not None
                else DEFAULT_PROJECT_CHAT_HISTORY_MAX_CHARS
            ),
            reranking_enabled=reranking_enabled if reranking_enabled is not None else False,
            reranker_backend=reranker_backend,
            reranker_model=reranker_model,
            reranker_candidate_multiplier=(
                reranker_candidate_multiplier
                if reranker_candidate_multiplier is not None
                else DEFAULT_PROJECT_RERANKER_CANDIDATE_MULTIPLIER
            ),
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
                f"{config_type}_api_key and "
                f"{config_type}_api_key_credential_id cannot both be set"
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
