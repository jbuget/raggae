from typing import Protocol
from uuid import UUID

from raggae.domain.entities.conversation import Conversation


class FavoriteConversationResult:
    """Conversation with its project name, for cross-project favorites listing."""

    def __init__(self, conversation: Conversation, project_name: str) -> None:
        self.conversation = conversation
        self.project_name = project_name


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

    async def toggle_favorite(self, conversation_id: UUID) -> Conversation: ...

    async def find_favorites_by_user(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FavoriteConversationResult]: ...
