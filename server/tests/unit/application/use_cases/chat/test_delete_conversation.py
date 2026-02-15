from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.chat.delete_conversation import DeleteConversation
from raggae.domain.entities.conversation import Conversation
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestDeleteConversation:
    async def test_delete_conversation_success(self) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        conversation_id = uuid4()
        project_repository = AsyncMock()
        conversation_repository = AsyncMock()
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
        use_case = DeleteConversation(
            project_repository=project_repository,
            conversation_repository=conversation_repository,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # Then
        conversation_repository.delete.assert_awaited_once_with(conversation_id)

    async def test_delete_conversation_unknown_project_raises_error(self) -> None:
        # Given
        project_repository = AsyncMock()
        conversation_repository = AsyncMock()
        project_repository.find_by_id.return_value = None
        use_case = DeleteConversation(
            project_repository=project_repository,
            conversation_repository=conversation_repository,
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=uuid4(),
                conversation_id=uuid4(),
                user_id=uuid4(),
            )

    async def test_delete_conversation_unknown_conversation_raises_error(self) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        project_repository = AsyncMock()
        conversation_repository = AsyncMock()
        project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        conversation_repository.find_by_id.return_value = None
        use_case = DeleteConversation(
            project_repository=project_repository,
            conversation_repository=conversation_repository,
        )

        # When / Then
        with pytest.raises(ConversationNotFoundError):
            await use_case.execute(
                project_id=project_id,
                conversation_id=uuid4(),
                user_id=user_id,
            )
