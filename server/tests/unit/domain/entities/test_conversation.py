from datetime import UTC, datetime
from uuid import uuid4

from raggae.domain.entities.conversation import Conversation


class TestConversation:
    def test_is_favorite_defaults_to_false(self) -> None:
        # Given / When
        conversation = Conversation(
            id=uuid4(),
            project_id=uuid4(),
            user_id=uuid4(),
            created_at=datetime.now(UTC),
        )

        # Then
        assert conversation.is_favorite is False

    def test_is_favorite_can_be_set_to_true(self) -> None:
        # Given / When
        conversation = Conversation(
            id=uuid4(),
            project_id=uuid4(),
            user_id=uuid4(),
            created_at=datetime.now(UTC),
            is_favorite=True,
        )

        # Then
        assert conversation.is_favorite is True
