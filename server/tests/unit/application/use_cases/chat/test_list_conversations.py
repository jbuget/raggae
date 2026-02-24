from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.use_cases.chat.list_conversations import ListConversations
from raggae.domain.entities.conversation import Conversation
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestListConversations:
    async def test_list_conversations_success(self) -> None:
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
        conversation_repository.find_by_project_and_user.return_value = [
            Conversation(
                id=uuid4(),
                project_id=project_id,
                user_id=user_id,
                created_at=datetime.now(UTC),
            )
        ]
        use_case = ListConversations(
            project_repository=project_repository,
            conversation_repository=conversation_repository,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            limit=10,
            offset=5,
        )

        # Then
        conversation_repository.find_by_project_and_user.assert_awaited_once_with(
            project_id=project_id,
            user_id=user_id,
            limit=10,
            offset=5,
        )
        assert len(result) == 1

    async def test_list_conversations_unknown_project_raises_error(self) -> None:
        # Given
        project_repository = AsyncMock()
        conversation_repository = AsyncMock()
        project_repository.find_by_id.return_value = None
        use_case = ListConversations(
            project_repository=project_repository,
            conversation_repository=conversation_repository,
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=uuid4(), user_id=uuid4())
