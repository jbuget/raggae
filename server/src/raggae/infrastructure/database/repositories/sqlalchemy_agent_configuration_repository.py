import os
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.agent_configuration import SYSTEM_OWNER_ID, AgentConfiguration
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.infrastructure.database.models.agent_configuration_model import AgentConfigurationModel


class SQLAlchemyAgentConfigurationRepository:
    """PostgreSQL agent configuration repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def find_by_owner(
        self, owner_id: UUID, owner_type: AgentConfigurationType
    ) -> AgentConfiguration | None:
        async with self._session_factory() as session:
            stmt = select(AgentConfigurationModel).where(
                AgentConfigurationModel.owner_id == owner_id,
                AgentConfigurationModel.owner_type == owner_type.value,
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_domain(model) if model else None

    async def find_app_defaults(self) -> AgentConfiguration | None:
        async with self._session_factory() as session:
            stmt = select(AgentConfigurationModel).where(
                AgentConfigurationModel.owner_type == AgentConfigurationType.APP.value,
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is not None:
                return self._to_domain(model)
        return self._fallback_from_env()

    async def save(self, config: AgentConfiguration) -> None:
        async with self._session_factory() as session:
            stmt = select(AgentConfigurationModel).where(
                AgentConfigurationModel.owner_id == config.owner_id,
                AgentConfigurationModel.owner_type == config.type.value,
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                model = AgentConfigurationModel(
                    id=config.id,
                    owner_id=config.owner_id,
                    owner_type=config.type.value,
                )
                session.add(model)
            model.embedding_backend = config.embedding_backend
            model.embedding_model = config.embedding_model
            model.embedding_api_key_credential_id = config.embedding_api_key_credential_id
            model.llm_backend = config.llm_backend
            model.llm_model = config.llm_model
            model.llm_api_key_credential_id = config.llm_api_key_credential_id
            model.chunking_strategy = config.chunking_strategy
            model.parent_child_chunking = config.parent_child_chunking
            model.retrieval_strategy = config.retrieval_strategy
            model.retrieval_top_k = config.retrieval_top_k
            model.retrieval_min_score = config.retrieval_min_score
            model.reranking_enabled = config.reranking_enabled
            model.reranker_backend = config.reranker_backend
            model.reranker_model = config.reranker_model
            model.reranker_candidate_multiplier = config.reranker_candidate_multiplier
            model.chat_history_window_size = config.chat_history_window_size
            model.chat_history_max_chars = config.chat_history_max_chars
            await session.commit()

    async def delete_by_owner(self, owner_id: UUID, owner_type: AgentConfigurationType) -> None:
        async with self._session_factory() as session:
            stmt = delete(AgentConfigurationModel).where(
                AgentConfigurationModel.owner_id == owner_id,
                AgentConfigurationModel.owner_type == owner_type.value,
            )
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    def _to_domain(model: AgentConfigurationModel) -> AgentConfiguration:
        return AgentConfiguration(
            id=model.id,
            owner_id=model.owner_id,
            type=AgentConfigurationType(model.owner_type),
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

    @staticmethod
    def _fallback_from_env() -> AgentConfiguration | None:
        def env(key: str) -> str | None:
            v = os.environ.get(key)
            return v if v else None

        def env_int(key: str, default: int) -> int:
            try:
                return int(os.environ.get(key, default))
            except (ValueError, TypeError):
                return default

        def env_float(key: str, default: float) -> float:
            try:
                return float(os.environ.get(key, default))
            except (ValueError, TypeError):
                return default

        return AgentConfiguration(
            id=uuid4(),
            owner_id=SYSTEM_OWNER_ID,
            type=AgentConfigurationType.APP,
            embedding_backend=env("DEFAULT_EMBEDDING_PROVIDER"),
            embedding_model=env("DEFAULT_EMBEDDING_MODEL"),
            llm_backend=env("DEFAULT_LLM_PROVIDER"),
            llm_model=env("DEFAULT_LLM_MODEL"),
            retrieval_strategy=env("RETRIEVAL_DEFAULT_STRATEGY") or "hybrid",
            retrieval_top_k=env_int("RETRIEVAL_DEFAULT_CHUNK_LIMIT", 8),
            retrieval_min_score=env_float("RETRIEVAL_MIN_SCORE", 0.3),
            reranker_backend=env("RERANKER_BACKEND"),
            reranker_model=env("RERANKER_MODEL"),
            reranker_candidate_multiplier=env_int("RERANKER_CANDIDATE_MULTIPLIER", 3),
            chat_history_window_size=env_int("CHAT_HISTORY_WINDOW_SIZE", 8),
            chat_history_max_chars=env_int("CHAT_HISTORY_MAX_CHARS", 4000),
        )
