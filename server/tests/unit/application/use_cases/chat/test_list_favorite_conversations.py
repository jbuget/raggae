from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from raggae.application.interfaces.repositories.conversation_repository import FavoriteConversationResult
from raggae.application.use_cases.chat.list_favorite_conversations import ListFavoriteConversations
from raggae.domain.entities.conversation import Conversation


class TestListFavoriteConversations:
    async def test_returns_favorites_for_user(self) -> None:
        # Given
        user_id = uuid4()
        conv1 = Conversation(
            id=uuid4(),
            project_id=uuid4(),
            user_id=user_id,
            created_at=datetime.now(UTC),
            is_favorite=True,
        )
        conv2 = Conversation(
            id=uuid4(),
            project_id=uuid4(),
            user_id=user_id,
            created_at=datetime.now(UTC),
            is_favorite=True,
        )
        conversation_repository = AsyncMock()
        conversation_repository.find_favorites_by_user.return_value = [
            FavoriteConversationResult(conversation=conv1, project_name="Project A"),
            FavoriteConversationResult(conversation=conv2, project_name="Project B"),
        ]
        use_case = ListFavoriteConversations(conversation_repository=conversation_repository)

        # When
        results = await use_case.execute(user_id=user_id, limit=50, offset=0)

        # Then
        assert len(results) == 2
        assert results[0].project_name == "Project A"
        assert results[1].project_name == "Project B"
        conversation_repository.find_favorites_by_user.assert_awaited_once_with(
            user_id=user_id, limit=50, offset=0
        )

    async def test_returns_empty_list_when_no_favorites(self) -> None:
        # Given
        conversation_repository = AsyncMock()
        conversation_repository.find_favorites_by_user.return_value = []
        use_case = ListFavoriteConversations(conversation_repository=conversation_repository)

        # When
        results = await use_case.execute(user_id=uuid4(), limit=50, offset=0)

        # Then
        assert results == []
