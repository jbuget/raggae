from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from raggae.domain.entities.agent_configuration import AgentConfiguration, SYSTEM_OWNER_ID
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_agent_configuration_repository import (
    SQLAlchemyAgentConfigurationRepository,
)


class TestSQLAlchemyAgentConfigurationRepository:
    @pytest.fixture
    async def session_factory(self) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(
            "postgresql+asyncpg://test:test@localhost:5433/raggae_test",
            echo=False,
        )
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
        except Exception as exc:  # pragma: no cover - environment dependent
            pytest.skip(f"PostgreSQL test database is not reachable: {exc}")

        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        yield factory

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    @pytest.mark.integration
    async def test_integration_save_and_find_by_owner(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repo = SQLAlchemyAgentConfigurationRepository(session_factory=session_factory)
        owner_id = uuid4()
        config = AgentConfiguration(
            id=uuid4(),
            owner_id=owner_id,
            type=AgentConfigurationType.PROJECT,
            embedding_backend="openai",
            embedding_model="text-embedding-3-small",
            llm_backend="openai",
            llm_model="gpt-4o",
            retrieval_strategy="hybrid",
            retrieval_top_k=10,
            retrieval_min_score=0.4,
            reranking_enabled=True,
            reranker_backend="cross_encoder",
            reranker_candidate_multiplier=3,
            chat_history_window_size=8,
            chat_history_max_chars=4000,
        )

        # When
        await repo.save(config)
        found = await repo.find_by_owner(owner_id, AgentConfigurationType.PROJECT)

        # Then
        assert found is not None
        assert found.id == config.id
        assert found.owner_id == owner_id
        assert found.type == AgentConfigurationType.PROJECT
        assert found.embedding_backend == "openai"
        assert found.embedding_model == "text-embedding-3-small"
        assert found.llm_backend == "openai"
        assert found.llm_model == "gpt-4o"
        assert found.retrieval_strategy == "hybrid"
        assert found.retrieval_top_k == 10
        assert found.retrieval_min_score == 0.4
        assert found.reranking_enabled is True
        assert found.reranker_backend == "cross_encoder"
        assert found.reranker_candidate_multiplier == 3
        assert found.chat_history_window_size == 8
        assert found.chat_history_max_chars == 4000

    @pytest.mark.integration
    async def test_integration_find_by_owner_returns_none_when_missing(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        repo = SQLAlchemyAgentConfigurationRepository(session_factory=session_factory)
        assert await repo.find_by_owner(uuid4(), AgentConfigurationType.USER) is None

    @pytest.mark.integration
    async def test_integration_save_updates_existing_config(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repo = SQLAlchemyAgentConfigurationRepository(session_factory=session_factory)
        owner_id = uuid4()
        config_id = uuid4()
        config_v1 = AgentConfiguration(
            id=config_id,
            owner_id=owner_id,
            type=AgentConfigurationType.USER,
            llm_backend="openai",
        )
        await repo.save(config_v1)

        # When — save new config with same owner_id+type but different fields
        config_v2 = AgentConfiguration(
            id=config_id,
            owner_id=owner_id,
            type=AgentConfigurationType.USER,
            llm_backend="ollama",
            llm_model="mistral",
        )
        await repo.save(config_v2)
        found = await repo.find_by_owner(owner_id, AgentConfigurationType.USER)

        # Then
        assert found is not None
        assert found.llm_backend == "ollama"
        assert found.llm_model == "mistral"

    @pytest.mark.integration
    async def test_integration_delete_by_owner(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repo = SQLAlchemyAgentConfigurationRepository(session_factory=session_factory)
        owner_id = uuid4()
        config = AgentConfiguration(
            id=uuid4(),
            owner_id=owner_id,
            type=AgentConfigurationType.ORGA,
            llm_backend="openai",
        )
        await repo.save(config)

        # When
        await repo.delete_by_owner(owner_id, AgentConfigurationType.ORGA)

        # Then
        assert await repo.find_by_owner(owner_id, AgentConfigurationType.ORGA) is None

    @pytest.mark.integration
    async def test_integration_find_app_defaults_returns_app_line(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repo = SQLAlchemyAgentConfigurationRepository(session_factory=session_factory)
        app_config = AgentConfiguration(
            id=uuid4(),
            owner_id=SYSTEM_OWNER_ID,
            type=AgentConfigurationType.APP,
            embedding_backend="openai",
            llm_backend="openai",
            llm_model="gpt-4o-mini",
        )
        await repo.save(app_config)

        # When
        found = await repo.find_app_defaults()

        # Then
        assert found is not None
        assert found.type == AgentConfigurationType.APP
        assert found.owner_id == SYSTEM_OWNER_ID
        assert found.embedding_backend == "openai"
        assert found.llm_model == "gpt-4o-mini"

    @pytest.mark.integration
    async def test_integration_find_app_defaults_falls_back_to_env_when_no_row(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given — no APP row in DB
        repo = SQLAlchemyAgentConfigurationRepository(session_factory=session_factory)

        # When
        found = await repo.find_app_defaults()

        # Then — fallback returns an APP config built from env vars (never None)
        assert found is not None
        assert found.type == AgentConfigurationType.APP
        assert found.owner_id == SYSTEM_OWNER_ID

    @pytest.mark.integration
    async def test_integration_different_owner_types_are_independent(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repo = SQLAlchemyAgentConfigurationRepository(session_factory=session_factory)
        owner_id = uuid4()
        user_config = AgentConfiguration(
            id=uuid4(), owner_id=owner_id, type=AgentConfigurationType.USER, llm_backend="openai"
        )
        orga_config = AgentConfiguration(
            id=uuid4(), owner_id=owner_id, type=AgentConfigurationType.ORGA, llm_backend="ollama"
        )

        # When
        await repo.save(user_config)
        await repo.save(orga_config)

        # Then
        user_found = await repo.find_by_owner(owner_id, AgentConfigurationType.USER)
        orga_found = await repo.find_by_owner(owner_id, AgentConfigurationType.ORGA)
        assert user_found is not None and user_found.llm_backend == "openai"
        assert orga_found is not None and orga_found.llm_backend == "ollama"
