from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from raggae.domain.entities.user import User
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


class TestSQLAlchemyUserRepository:
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
    async def test_integration_save_find_by_id_and_email(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        repository = SQLAlchemyUserRepository(session_factory=session_factory)
        user = User(
            id=uuid4(),
            email="integration@example.com",
            hashed_password="hashed",
            full_name="Integration User",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        await repository.save(user)

        found_by_id = await repository.find_by_id(user.id)
        assert found_by_id is not None
        assert found_by_id.email == "integration@example.com"

        found_by_email = await repository.find_by_email("integration@example.com")
        assert found_by_email is not None
        assert found_by_email.id == user.id
