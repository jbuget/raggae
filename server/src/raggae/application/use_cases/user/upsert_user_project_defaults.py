from uuid import UUID

from raggae.application.constants import (
    SUPPORTED_CHUNKING_STRATEGIES,
    SUPPORTED_EMBEDDING_BACKENDS,
    SUPPORTED_LLM_BACKENDS,
    SUPPORTED_RERANKER_BACKENDS,
    SUPPORTED_RETRIEVAL_STRATEGIES,
)
from raggae.application.dto.user_project_defaults_dto import UserProjectDefaultsDTO
from raggae.application.interfaces.repositories.user_project_defaults_repository import (
    UserProjectDefaultsRepository,
)
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.domain.entities.user_project_defaults import UserProjectDefaults
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    InvalidProjectRerankerBackendError,
    InvalidProjectRetrievalStrategyError,
)
from raggae.domain.exceptions.user_exceptions import UserNotFoundError


class UpsertUserProjectDefaults:
    """Use Case: Create or replace project defaults for a user."""

    def __init__(
        self,
        user_repository: UserRepository,
        user_project_defaults_repository: UserProjectDefaultsRepository,
    ) -> None:
        self._user_repository = user_repository
        self._user_project_defaults_repository = user_project_defaults_repository

    async def execute(
        self,
        user_id: UUID,
        embedding_backend: str | None = None,
        embedding_model: str | None = None,
        embedding_api_key_credential_id: UUID | None = None,
        llm_backend: str | None = None,
        llm_model: str | None = None,
        llm_api_key_credential_id: UUID | None = None,
        chunking_strategy: str | None = None,
        parent_child_chunking: bool | None = None,
        retrieval_strategy: str | None = None,
        retrieval_top_k: int | None = None,
        retrieval_min_score: float | None = None,
        reranking_enabled: bool | None = None,
        reranker_backend: str | None = None,
        reranker_model: str | None = None,
        reranker_candidate_multiplier: int | None = None,
        chat_history_window_size: int | None = None,
        chat_history_max_chars: int | None = None,
    ) -> UserProjectDefaultsDTO:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")

        if embedding_backend is not None and embedding_backend not in SUPPORTED_EMBEDDING_BACKENDS:
            raise InvalidProjectEmbeddingBackendError(f"Unsupported embedding backend: {embedding_backend}")
        if llm_backend is not None and llm_backend not in SUPPORTED_LLM_BACKENDS:
            raise InvalidProjectLLMBackendError(f"Unsupported LLM backend: {llm_backend}")
        if chunking_strategy is not None and chunking_strategy not in SUPPORTED_CHUNKING_STRATEGIES:
            raise ValueError(f"Unsupported chunking strategy: {chunking_strategy}")
        if retrieval_strategy is not None and retrieval_strategy not in SUPPORTED_RETRIEVAL_STRATEGIES:
            raise InvalidProjectRetrievalStrategyError(
                f"Unsupported retrieval strategy: {retrieval_strategy}"
            )
        if reranker_backend is not None and reranker_backend not in SUPPORTED_RERANKER_BACKENDS:
            raise InvalidProjectRerankerBackendError(f"Unsupported reranker backend: {reranker_backend}")

        defaults = UserProjectDefaults(
            user_id=user_id,
            embedding_backend=embedding_backend,
            embedding_model=embedding_model,
            embedding_api_key_credential_id=embedding_api_key_credential_id,
            llm_backend=llm_backend,
            llm_model=llm_model,
            llm_api_key_credential_id=llm_api_key_credential_id,
            chunking_strategy=chunking_strategy,
            parent_child_chunking=parent_child_chunking,
            retrieval_strategy=retrieval_strategy,
            retrieval_top_k=retrieval_top_k,
            retrieval_min_score=retrieval_min_score,
            reranking_enabled=reranking_enabled,
            reranker_backend=reranker_backend,
            reranker_model=reranker_model,
            reranker_candidate_multiplier=reranker_candidate_multiplier,
            chat_history_window_size=chat_history_window_size,
            chat_history_max_chars=chat_history_max_chars,
        )
        await self._user_project_defaults_repository.save(defaults)
        return UserProjectDefaultsDTO.from_entity(defaults)
