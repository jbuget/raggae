from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.conversation import Conversation
from raggae.infrastructure.database.models.conversation_model import ConversationModel


class SQLAlchemyConversationRepository:
    """PostgreSQL conversation repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_or_create(self, project_id: UUID, user_id: UUID) -> Conversation:
        async with self._session_factory() as session:
            existing = (
                await session.execute(
                    select(ConversationModel).where(
                        ConversationModel.project_id == project_id,
                        ConversationModel.user_id == user_id,
                    )
                )
            ).scalars().first()
            if existing is not None:
                return Conversation(
                    id=existing.id,
                    project_id=existing.project_id,
                    user_id=existing.user_id,
                    created_at=existing.created_at,
                    title=existing.title,
                )

            model = ConversationModel(
                id=uuid4(),
                project_id=project_id,
                user_id=user_id,
                created_at=datetime.now(UTC),
                title="New conversation",
            )
            session.add(model)
            await session.commit()
            return Conversation(
                id=model.id,
                project_id=model.project_id,
                user_id=model.user_id,
                created_at=model.created_at,
                title=model.title,
            )

    async def find_by_id(self, conversation_id: UUID) -> Conversation | None:
        async with self._session_factory() as session:
            model = await session.get(ConversationModel, conversation_id)
            if model is None:
                return None
            return Conversation(
                id=model.id,
                project_id=model.project_id,
                user_id=model.user_id,
                created_at=model.created_at,
                title=model.title,
            )

    async def find_by_project_and_user(
        self,
        project_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        async with self._session_factory() as session:
            models = (
                await session.execute(
                    select(ConversationModel)
                    .where(
                        ConversationModel.project_id == project_id,
                        ConversationModel.user_id == user_id,
                    )
                    .order_by(ConversationModel.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                )
            ).scalars()
            return [
                Conversation(
                    id=model.id,
                    project_id=model.project_id,
                    user_id=model.user_id,
                    created_at=model.created_at,
                    title=model.title,
                )
                for model in models
            ]

    async def delete(self, conversation_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ConversationModel).where(ConversationModel.id == conversation_id)
            )
            await session.commit()

    async def update_title(self, conversation_id: UUID, title: str) -> None:
        async with self._session_factory() as session:
            model = await session.get(ConversationModel, conversation_id)
            if model is None:
                return
            model.title = title
            await session.commit()
