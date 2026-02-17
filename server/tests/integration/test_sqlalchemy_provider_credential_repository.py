from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from raggae.domain.entities.user import User
from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_provider_credential_repository import (
    SQLAlchemyProviderCredentialRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


class TestSQLAlchemyProviderCredentialRepository:
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
    async def test_integration_save_list_and_delete(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        user_id = uuid4()
        now = datetime.now(UTC)
        user_repository = SQLAlchemyUserRepository(session_factory=session_factory)
        repository = SQLAlchemyProviderCredentialRepository(session_factory=session_factory)
        await user_repository.save(
            User(
                id=user_id,
                email="provider-credential@example.com",
                hashed_password="hashed",
                full_name="Provider User",
                is_active=True,
                created_at=now,
            )
        )
        credential = UserModelProviderCredential(
            id=uuid4(),
            user_id=user_id,
            provider=ModelProvider("openai"),
            encrypted_api_key="encrypted-key-1",
            key_fingerprint="fingerprint-1",
            key_suffix="abcd",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        # When
        await repository.save(credential)
        listed = await repository.list_by_user_id(user_id)
        await repository.delete(credential.id, user_id)
        listed_after_delete = await repository.list_by_user_id(user_id)

        # Then
        assert len(listed) == 1
        assert listed[0].provider.value == "openai"
        assert listed[0].masked_key == "...abcd"
        assert listed_after_delete == []

    @pytest.mark.integration
    async def test_integration_set_active_for_user_provider_keeps_single_active(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        user_id = uuid4()
        now = datetime.now(UTC)
        user_repository = SQLAlchemyUserRepository(session_factory=session_factory)
        repository = SQLAlchemyProviderCredentialRepository(session_factory=session_factory)
        await user_repository.save(
            User(
                id=user_id,
                email="provider-credential-2@example.com",
                hashed_password="hashed",
                full_name="Provider User",
                is_active=True,
                created_at=now,
            )
        )
        first = UserModelProviderCredential(
            id=uuid4(),
            user_id=user_id,
            provider=ModelProvider("gemini"),
            encrypted_api_key="encrypted-key-1",
            key_fingerprint="fingerprint-1",
            key_suffix="1111",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        second = UserModelProviderCredential(
            id=uuid4(),
            user_id=user_id,
            provider=ModelProvider("gemini"),
            encrypted_api_key="encrypted-key-2",
            key_fingerprint="fingerprint-2",
            key_suffix="2222",
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        await repository.save(first)
        await repository.save(second)

        # When
        await repository.set_active(second.id, user_id)
        listed = await repository.list_by_user_id_and_provider(user_id, ModelProvider("gemini"))

        # Then
        active_credentials = [credential for credential in listed if credential.is_active]
        assert len(active_credentials) == 1
        assert active_credentials[0].id == second.id
