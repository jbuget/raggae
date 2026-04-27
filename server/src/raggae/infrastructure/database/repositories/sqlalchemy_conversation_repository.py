from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.application.interfaces.repositories.conversation_repository import FavoriteConversationResult
from raggae.domain.entities.conversation import Conversation
from raggae.infrastructure.database.models.conversation_model import ConversationModel
from raggae.infrastructure.database.models.project_model import ProjectModel


def _to_entity(model: ConversationModel) -> Conversation:
    return Conversation(
        id=model.id,
        project_id=model.project_id,
        user_id=model.user_id,
        created_at=model.created_at,
        title=model.title,
        is_favorite=model.is_favorite,
    )


class SQLAlchemyConversationRepository:
    """PostgreSQL conversation repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, project_id: UUID, user_id: UUID) -> Conversation:
        async with self._session_factory() as session:
            model = ConversationModel(
                id=uuid4(),
                project_id=project_id,
                user_id=user_id,
                created_at=datetime.now(UTC),
                title="New conversation",
            )
            session.add(model)
            await session.commit()
            return _to_entity(model)

    async def get_or_create(self, project_id: UUID, user_id: UUID) -> Conversation:
        async with self._session_factory() as session:
            existing = (
                (
                    await session.execute(
                        select(ConversationModel).where(
                            ConversationModel.project_id == project_id,
                            ConversationModel.user_id == user_id,
                        )
                    )
                )
                .scalars()
                .first()
            )
            if existing is not None:
                return _to_entity(existing)

            model = ConversationModel(
                id=uuid4(),
                project_id=project_id,
                user_id=user_id,
                created_at=datetime.now(UTC),
                title="New conversation",
            )
            session.add(model)
            await session.commit()
            return _to_entity(model)

    async def find_by_id(self, conversation_id: UUID) -> Conversation | None:
        async with self._session_factory() as session:
            model = await session.get(ConversationModel, conversation_id)
            if model is None:
                return None
            return _to_entity(model)

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
            return [_to_entity(model) for model in models]

    async def delete(self, conversation_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(delete(ConversationModel).where(ConversationModel.id == conversation_id))
            await session.commit()

    async def update_title(self, conversation_id: UUID, title: str) -> None:
        async with self._session_factory() as session:
            model = await session.get(ConversationModel, conversation_id)
            if model is None:
                return
            model.title = title
            await session.commit()

    async def toggle_favorite(self, conversation_id: UUID) -> Conversation:
        async with self._session_factory() as session:
            model = await session.get(ConversationModel, conversation_id)
            if model is None:
                from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError

                raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
            model.is_favorite = not model.is_favorite
            await session.commit()
            return _to_entity(model)

    async def find_favorites_by_user(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FavoriteConversationResult]:
        async with self._session_factory() as session:
            rows = (
                await session.execute(
                    select(ConversationModel, ProjectModel.name)
                    .join(ProjectModel, ConversationModel.project_id == ProjectModel.id)
                    .where(
                        ConversationModel.user_id == user_id,
                        ConversationModel.is_favorite.is_(True),
                    )
                    .order_by(ConversationModel.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                )
            ).all()
            return [
                FavoriteConversationResult(
                    conversation=_to_entity(conv_model),
                    project_name=project_name,
                )
                for conv_model, project_name in rows
            ]
