from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.message import Message
from raggae.infrastructure.database.models.message_model import MessageModel


class SQLAlchemyMessageRepository:
    """PostgreSQL message repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, message: Message) -> None:
        async with self._session_factory() as session:
            model = MessageModel(
                id=message.id,
                conversation_id=message.conversation_id,
                role=message.role,
                content=message.content,
                source_documents=message.source_documents,
                reliability_percent=message.reliability_percent,
                created_at=message.created_at,
            )
            session.add(model)
            await session.commit()

    async def find_by_conversation_id(
        self,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        async with self._session_factory() as session:
            models = (
                await session.execute(
                    select(MessageModel)
                    .where(MessageModel.conversation_id == conversation_id)
                    .order_by(MessageModel.created_at)
                    .offset(offset)
                    .limit(limit)
                )
            ).scalars()
            return [
                Message(
                    id=model.id,
                    conversation_id=model.conversation_id,
                    role=model.role,
                    content=model.content,
                    source_documents=model.source_documents,
                    reliability_percent=model.reliability_percent,
                    created_at=model.created_at,
                )
                for model in models
            ]

    async def count_by_conversation_id(self, conversation_id: UUID) -> int:
        async with self._session_factory() as session:
            value = (
                await session.execute(
                    select(func.count())
                    .select_from(MessageModel)
                    .where(MessageModel.conversation_id == conversation_id)
                )
            ).scalar_one()
            return int(value)

    async def find_latest_by_conversation_id(
        self,
        conversation_id: UUID,
    ) -> Message | None:
        async with self._session_factory() as session:
            model = (
                (
                    await session.execute(
                        select(MessageModel)
                        .where(MessageModel.conversation_id == conversation_id)
                        .order_by(MessageModel.created_at.desc())
                        .limit(1)
                    )
                )
                .scalars()
                .first()
            )
            if model is None:
                return None
            return Message(
                id=model.id,
                conversation_id=model.conversation_id,
                role=model.role,
                content=model.content,
                source_documents=model.source_documents,
                reliability_percent=model.reliability_percent,
                created_at=model.created_at,
            )
