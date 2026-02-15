from uuid import UUID

from raggae.domain.entities.message import Message


class InMemoryMessageRepository:
    """In-memory message repository for testing."""

    def __init__(self) -> None:
        self._messages: dict[UUID, Message] = {}

    async def save(self, message: Message) -> None:
        self._messages[message.id] = message

    async def find_by_conversation_id(
        self,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        messages = [
            message
            for message in self._messages.values()
            if message.conversation_id == conversation_id
        ]
        messages.sort(key=lambda item: item.created_at)
        return messages[offset : offset + limit]

    async def count_by_conversation_id(self, conversation_id: UUID) -> int:
        return len(
            [
                message
                for message in self._messages.values()
                if message.conversation_id == conversation_id
            ]
        )

    async def find_latest_by_conversation_id(
        self,
        conversation_id: UUID,
    ) -> Message | None:
        messages = [
            message
            for message in self._messages.values()
            if message.conversation_id == conversation_id
        ]
        if not messages:
            return None
        return max(messages, key=lambda item: item.created_at)
