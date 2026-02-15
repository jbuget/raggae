from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.chat.get_conversation import GetConversation
from raggae.domain.entities.conversation import Conversation
from raggae.domain.entities.message import Message
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestGetConversation:
    async def test_get_conversation_success(self) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        conversation_id = uuid4()
        project_repository = AsyncMock()
        conversation_repository = AsyncMock()
        message_repository = AsyncMock()
        project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        conversation_repository.find_by_id.return_value = Conversation(
            id=conversation_id,
            project_id=project_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
        )
        message_repository.count_by_conversation_id.return_value = 2
        message_repository.find_latest_by_conversation_id.return_value = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role="assistant",
            content="latest",
            created_at=datetime.now(UTC),
        )
        use_case = GetConversation(
            project_repository=project_repository,
            conversation_repository=conversation_repository,
            message_repository=message_repository,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # Then
        assert result.id == conversation_id
        assert result.message_count == 2
        assert result.last_message is not None
        assert result.last_message.content == "latest"

    async def test_get_conversation_unknown_project_raises_error(self) -> None:
        # Given
        use_case = GetConversation(
            project_repository=AsyncMock(find_by_id=AsyncMock(return_value=None)),
            conversation_repository=AsyncMock(),
            message_repository=AsyncMock(),
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=uuid4(),
                conversation_id=uuid4(),
                user_id=uuid4(),
            )

    async def test_get_conversation_unknown_conversation_raises_error(self) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        conversation_repository = AsyncMock()
        conversation_repository.find_by_id.return_value = None
        use_case = GetConversation(
            project_repository=project_repository,
            conversation_repository=conversation_repository,
            message_repository=AsyncMock(),
        )

        # When / Then
        with pytest.raises(ConversationNotFoundError):
            await use_case.execute(
                project_id=project_id,
                conversation_id=uuid4(),
                user_id=user_id,
            )
