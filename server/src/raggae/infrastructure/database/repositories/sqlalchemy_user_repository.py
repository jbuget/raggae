from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.user import User
from raggae.infrastructure.database.models.user_model import UserModel


class SQLAlchemyUserRepository:
    """PostgreSQL user repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, user: User) -> None:
        async with self._session_factory() as session:
            model = await session.get(UserModel, user.id)
            if model is None:
                model = UserModel(
                    id=user.id,
                    email=user.email,
                    hashed_password=user.hashed_password,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    created_at=user.created_at,
                )
                session.add(model)
            else:
                model.email = user.email
                model.hashed_password = user.hashed_password
                model.full_name = user.full_name
                model.is_active = user.is_active
            await session.commit()

    async def find_by_id(self, user_id: UUID) -> User | None:
        async with self._session_factory() as session:
            model = await session.get(UserModel, user_id)
            if model is None:
                return None
            return User(
                id=model.id,
                email=model.email,
                hashed_password=model.hashed_password,
                full_name=model.full_name,
                is_active=model.is_active,
                created_at=model.created_at,
            )

    async def find_by_email(self, email: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(select(UserModel).where(UserModel.email == email))
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return User(
                id=model.id,
                email=model.email,
                hashed_password=model.hashed_password,
                full_name=model.full_name,
                is_active=model.is_active,
                created_at=model.created_at,
            )
