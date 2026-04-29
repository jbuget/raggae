from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.chat.toggle_favorite_conversation import ToggleFavoriteConversation
from raggae.domain.entities.conversation import Conversation
from raggae.domain.exceptions.conversation_exceptions import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
)


class TestToggleFavoriteConversation:
    async def test_toggle_favorite_sets_is_favorite_to_true(self) -> None:
        # Given
        user_id = uuid4()
        conversation_id = uuid4()
        conversation_repository = AsyncMock()
        conversation_repository.find_by_id.return_value = Conversation(
            id=conversation_id,
            project_id=uuid4(),
            user_id=user_id,
            created_at=datetime.now(UTC),
            is_favorite=False,
        )
        conversation_repository.toggle_favorite.return_value = Conversation(
            id=conversation_id,
            project_id=uuid4(),
            user_id=user_id,
            created_at=datetime.now(UTC),
            is_favorite=True,
        )
        use_case = ToggleFavoriteConversation(conversation_repository=conversation_repository)

        # When
        result = await use_case.execute(conversation_id=conversation_id, user_id=user_id)

        # Then
        assert result.is_favorite is True
        conversation_repository.toggle_favorite.assert_awaited_once_with(conversation_id)

    async def test_toggle_favorite_sets_is_favorite_to_false(self) -> None:
        # Given
        user_id = uuid4()
        conversation_id = uuid4()
        conversation_repository = AsyncMock()
        conversation_repository.find_by_id.return_value = Conversation(
            id=conversation_id,
            project_id=uuid4(),
            user_id=user_id,
            created_at=datetime.now(UTC),
            is_favorite=True,
        )
        conversation_repository.toggle_favorite.return_value = Conversation(
            id=conversation_id,
            project_id=uuid4(),
            user_id=user_id,
            created_at=datetime.now(UTC),
            is_favorite=False,
        )
        use_case = ToggleFavoriteConversation(conversation_repository=conversation_repository)

        # When
        result = await use_case.execute(conversation_id=conversation_id, user_id=user_id)

        # Then
        assert result.is_favorite is False

    async def test_toggle_favorite_unknown_conversation_raises_error(self) -> None:
        # Given
        conversation_repository = AsyncMock()
        conversation_repository.find_by_id.return_value = None
        use_case = ToggleFavoriteConversation(conversation_repository=conversation_repository)

        # When / Then
        with pytest.raises(ConversationNotFoundError):
            await use_case.execute(conversation_id=uuid4(), user_id=uuid4())

    async def test_toggle_favorite_non_owner_raises_access_denied(self) -> None:
        # Given
        conversation_repository = AsyncMock()
        conversation_repository.find_by_id.return_value = Conversation(
            id=uuid4(),
            project_id=uuid4(),
            user_id=uuid4(),
            created_at=datetime.now(UTC),
        )
        use_case = ToggleFavoriteConversation(conversation_repository=conversation_repository)

        # When / Then
        with pytest.raises(ConversationAccessDeniedError):
            await use_case.execute(conversation_id=uuid4(), user_id=uuid4())
