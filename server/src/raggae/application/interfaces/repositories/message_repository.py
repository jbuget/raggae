from typing import Protocol
from uuid import UUID

from raggae.domain.entities.message import Message


class MessageRepository(Protocol):
    """Interface for message persistence."""

    async def save(self, message: Message) -> None: ...

    async def find_by_conversation_id(
        self,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]: ...

    async def count_by_conversation_id(self, conversation_id: UUID) -> int: ...

    async def find_latest_by_conversation_id(
        self, conversation_id: UUID
    ) -> Message | None: ...
