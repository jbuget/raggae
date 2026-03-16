from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.domain.entities.message import Message


class TestMessage:
    def test_create_message_with_valid_role(self) -> None:
        # Given / When
        message = Message(
            id=uuid4(),
            conversation_id=uuid4(),
            role="user",
            content="hello",
            created_at=datetime.now(UTC),
        )

        # Then
        assert message.role == "user"

    def test_create_message_with_invalid_role_raises_error(self) -> None:
        # Given / When / Then
        with pytest.raises(ValueError):
            Message(
                id=uuid4(),
                conversation_id=uuid4(),
                role="bad",
                content="hello",
                created_at=datetime.now(UTC),
            )
