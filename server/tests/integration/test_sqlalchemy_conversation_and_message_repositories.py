from datetime import UTC, datetime
from uuid import uuid4

import pytest
from raggae.domain.entities.message import Message
from raggae.domain.entities.project import Project
from raggae.domain.entities.user import User
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.models.conversation_model import ConversationModel
from raggae.infrastructure.database.repositories.sqlalchemy_conversation_repository import (
    SQLAlchemyConversationRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_message_repository import (
    SQLAlchemyMessageRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class TestSQLAlchemyConversationAndMessageRepositories:
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
    async def test_integration_get_or_create_conversation_and_save_messages(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        user_repository = SQLAlchemyUserRepository(session_factory=session_factory)
        project_repository = SQLAlchemyProjectRepository(session_factory=session_factory)
        conversation_repository = SQLAlchemyConversationRepository(session_factory=session_factory)
        message_repository = SQLAlchemyMessageRepository(session_factory=session_factory)

        await user_repository.save(
            User(
                id=user_id,
                email="user@example.com",
                hashed_password="hashed",
                full_name="User",
                is_active=True,
                created_at=datetime.now(UTC),
            )
        )
        await project_repository.save(
            Project(
                id=project_id,
                user_id=user_id,
                name="Project",
                description="",
                system_prompt="",
                is_published=False,
                created_at=datetime.now(UTC),
            )
        )

        # When
        conversation = await conversation_repository.get_or_create(
            project_id=project_id,
            user_id=user_id,
        )
        same_conversation = await conversation_repository.get_or_create(
            project_id=project_id,
            user_id=user_id,
        )
        await message_repository.save(
            Message(
                id=uuid4(),
                conversation_id=conversation.id,
                role="user",
                content="hello",
                created_at=datetime.now(UTC),
            )
        )
        await message_repository.save(
            Message(
                id=uuid4(),
                conversation_id=conversation.id,
                role="assistant",
                content="world",
                source_documents=[
                    {
                        "document_id": str(uuid4()),
                        "document_file_name": "knowledge.md",
                    }
                ],
                created_at=datetime.now(UTC),
            )
        )
        messages = await message_repository.find_by_conversation_id(conversation.id)

        # Then
        assert same_conversation.id == conversation.id
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
        assert messages[1].source_documents is not None

    @pytest.mark.integration
    async def test_integration_find_by_project_and_user_sorted_and_delete_cascade(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        user_repository = SQLAlchemyUserRepository(session_factory=session_factory)
        project_repository = SQLAlchemyProjectRepository(session_factory=session_factory)
        conversation_repository = SQLAlchemyConversationRepository(session_factory=session_factory)
        message_repository = SQLAlchemyMessageRepository(session_factory=session_factory)

        await user_repository.save(
            User(
                id=user_id,
                email="user2@example.com",
                hashed_password="hashed",
                full_name="User 2",
                is_active=True,
                created_at=datetime.now(UTC),
            )
        )
        await project_repository.save(
            Project(
                id=project_id,
                user_id=user_id,
                name="Project 2",
                description="",
                system_prompt="",
                is_published=False,
                created_at=datetime.now(UTC),
            )
        )

        conv_a_id = uuid4()
        conv_b_id = uuid4()
        async with session_factory() as session:
            session.add(
                ConversationModel(
                    id=conv_a_id,
                    project_id=project_id,
                    user_id=user_id,
                    created_at=datetime(2026, 1, 1, tzinfo=UTC),
                )
            )
            session.add(
                ConversationModel(
                    id=conv_b_id,
                    project_id=project_id,
                    user_id=user_id,
                    created_at=datetime(2026, 1, 2, tzinfo=UTC),
                )
            )
            await session.commit()

        await message_repository.save(
            Message(
                id=uuid4(),
                conversation_id=conv_b_id,
                role="user",
                content="hello",
                created_at=datetime.now(UTC),
            )
        )

        # When
        conversations = await conversation_repository.find_by_project_and_user(
            project_id=project_id,
            user_id=user_id,
        )
        await conversation_repository.delete(conv_b_id)
        messages_after_delete = await message_repository.find_by_conversation_id(conv_b_id)

        # Then
        assert [conversation.id for conversation in conversations][:2] == [conv_b_id, conv_a_id]
        assert messages_after_delete == []
