from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.user_project_defaults import UserProjectDefaults
from raggae.infrastructure.database.models.user_project_defaults_model import UserProjectDefaultsModel


class SQLAlchemyUserProjectDefaultsRepository:
    """PostgreSQL user project defaults repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def find_by_user_id(self, user_id: UUID) -> UserProjectDefaults | None:
        async with self._session_factory() as session:
            model = await session.get(UserProjectDefaultsModel, user_id)
            if model is None:
                return None
            return self._to_domain(model)

    async def save(self, defaults: UserProjectDefaults) -> None:
        async with self._session_factory() as session:
            model = await session.get(UserProjectDefaultsModel, defaults.user_id)
            if model is None:
                model = UserProjectDefaultsModel(user_id=defaults.user_id)
                session.add(model)
            model.embedding_backend = defaults.embedding_backend
            model.embedding_model = defaults.embedding_model
            model.embedding_api_key_credential_id = defaults.embedding_api_key_credential_id
            model.llm_backend = defaults.llm_backend
            model.llm_model = defaults.llm_model
            model.llm_api_key_credential_id = defaults.llm_api_key_credential_id
            model.chunking_strategy = defaults.chunking_strategy
            model.parent_child_chunking = defaults.parent_child_chunking
            model.retrieval_strategy = defaults.retrieval_strategy
            model.retrieval_top_k = defaults.retrieval_top_k
            model.retrieval_min_score = defaults.retrieval_min_score
            model.reranking_enabled = defaults.reranking_enabled
            model.reranker_backend = defaults.reranker_backend
            model.reranker_model = defaults.reranker_model
            model.reranker_candidate_multiplier = defaults.reranker_candidate_multiplier
            model.chat_history_window_size = defaults.chat_history_window_size
            model.chat_history_max_chars = defaults.chat_history_max_chars
            await session.commit()

    @staticmethod
    def _to_domain(model: UserProjectDefaultsModel) -> UserProjectDefaults:
        return UserProjectDefaults(
            user_id=model.user_id,
            embedding_backend=model.embedding_backend,
            embedding_model=model.embedding_model,
            embedding_api_key_credential_id=model.embedding_api_key_credential_id,
            llm_backend=model.llm_backend,
            llm_model=model.llm_model,
            llm_api_key_credential_id=model.llm_api_key_credential_id,
            chunking_strategy=model.chunking_strategy,
            parent_child_chunking=model.parent_child_chunking,
            retrieval_strategy=model.retrieval_strategy,
            retrieval_top_k=model.retrieval_top_k,
            retrieval_min_score=model.retrieval_min_score,
            reranking_enabled=model.reranking_enabled,
            reranker_backend=model.reranker_backend,
            reranker_model=model.reranker_model,
            reranker_candidate_multiplier=model.reranker_candidate_multiplier,
            chat_history_window_size=model.chat_history_window_size,
            chat_history_max_chars=model.chat_history_max_chars,
        )
