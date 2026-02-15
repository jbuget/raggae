from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.chat.list_conversation_messages import (
    ListConversationMessages,
)
from raggae.domain.entities.conversation import Conversation
from raggae.domain.entities.message import Message
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestListConversationMessages:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_conversation_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_message_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(
        self,
        mock_project_repository: AsyncMock,
        mock_conversation_repository: AsyncMock,
        mock_message_repository: AsyncMock,
    ) -> ListConversationMessages:
        return ListConversationMessages(
            project_repository=mock_project_repository,
            conversation_repository=mock_conversation_repository,
            message_repository=mock_message_repository,
        )

    async def test_list_conversation_messages_success(
        self,
        use_case: ListConversationMessages,
        mock_project_repository: AsyncMock,
        mock_conversation_repository: AsyncMock,
        mock_message_repository: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        conversation_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_conversation_repository.find_by_id.return_value = Conversation(
            id=conversation_id,
            project_id=project_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
        )
        mock_message_repository.find_by_conversation_id.return_value = [
            Message(
                id=uuid4(),
                conversation_id=conversation_id,
                role="user",
                content="hello",
                created_at=datetime.now(UTC),
            ),
            Message(
                id=uuid4(),
                conversation_id=conversation_id,
                role="assistant",
                content="world",
                created_at=datetime.now(UTC),
            ),
        ]

        # When
        result = await use_case.execute(
            project_id=project_id,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # Then
        mock_message_repository.find_by_conversation_id.assert_awaited_once_with(
            conversation_id,
            limit=50,
            offset=0,
        )
        assert len(result) == 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    async def test_list_conversation_messages_unknown_project_raises_error(
        self,
        use_case: ListConversationMessages,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=uuid4(),
                conversation_id=uuid4(),
                user_id=uuid4(),
            )

    async def test_list_conversation_messages_unknown_conversation_raises_error(
        self,
        use_case: ListConversationMessages,
        mock_project_repository: AsyncMock,
        mock_conversation_repository: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_conversation_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(ConversationNotFoundError):
            await use_case.execute(
                project_id=project_id,
                conversation_id=uuid4(),
                user_id=user_id,
            )
