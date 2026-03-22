from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.organization_default_config import OrganizationDefaultConfig
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.database.models.organization_default_config_model import (
    OrganizationDefaultConfigModel,
)


class SQLAlchemyOrganizationDefaultConfigRepository:
    """PostgreSQL organization default config repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def find_by_organization_id(self, organization_id: UUID) -> OrganizationDefaultConfig | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrganizationDefaultConfigModel).where(
                    OrganizationDefaultConfigModel.organization_id == organization_id
                )
            )
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_entity(model)

    async def save(self, config: OrganizationDefaultConfig) -> None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrganizationDefaultConfigModel).where(
                    OrganizationDefaultConfigModel.organization_id == config.organization_id
                )
            )
            model = result.scalar_one_or_none()
            if model is None:
                model = OrganizationDefaultConfigModel(
                    id=config.id,
                    organization_id=config.organization_id,
                )
                session.add(model)
            model.embedding_backend = config.embedding_backend
            model.llm_backend = config.llm_backend
            model.chunking_strategy = config.chunking_strategy.value if config.chunking_strategy else None
            model.retrieval_strategy = config.retrieval_strategy
            model.retrieval_top_k = config.retrieval_top_k
            model.retrieval_min_score = config.retrieval_min_score
            model.reranking_enabled = config.reranking_enabled
            model.reranker_backend = config.reranker_backend
            model.org_embedding_api_key_credential_id = config.org_embedding_api_key_credential_id
            model.org_llm_api_key_credential_id = config.org_llm_api_key_credential_id
            model.updated_at = config.updated_at
            await session.commit()

    @staticmethod
    def _to_entity(model: OrganizationDefaultConfigModel) -> OrganizationDefaultConfig:
        return OrganizationDefaultConfig(
            id=model.id,
            organization_id=model.organization_id,
            embedding_backend=model.embedding_backend,
            llm_backend=model.llm_backend,
            chunking_strategy=ChunkingStrategy(model.chunking_strategy) if model.chunking_strategy else None,
            retrieval_strategy=model.retrieval_strategy,
            retrieval_top_k=model.retrieval_top_k,
            retrieval_min_score=model.retrieval_min_score,
            reranking_enabled=model.reranking_enabled,
            reranker_backend=model.reranker_backend,
            org_embedding_api_key_credential_id=model.org_embedding_api_key_credential_id,
            org_llm_api_key_credential_id=model.org_llm_api_key_credential_id,
            updated_at=model.updated_at,
        )
