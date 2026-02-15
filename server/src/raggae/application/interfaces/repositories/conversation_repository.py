from typing import Protocol
from uuid import UUID

from raggae.domain.entities.conversation import Conversation


class ConversationRepository(Protocol):
    """Interface for conversation persistence."""

    async def create(self, project_id: UUID, user_id: UUID) -> Conversation: ...

    async def get_or_create(self, project_id: UUID, user_id: UUID) -> Conversation: ...

    async def find_by_id(self, conversation_id: UUID) -> Conversation | None: ...

    async def find_by_project_and_user(
        self,
        project_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]: ...

    async def delete(self, conversation_id: UUID) -> None: ...

    async def update_title(self, conversation_id: UUID, title: str) -> None: ...
