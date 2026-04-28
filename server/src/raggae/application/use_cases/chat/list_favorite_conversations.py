from uuid import UUID

from raggae.application.dto.favorite_conversation_dto import FavoriteConversationResult
from raggae.application.interfaces.repositories.conversation_repository import ConversationRepository


class ListFavoriteConversations:
    """Use Case: List all favorite conversations for the current user across all projects."""

    def __init__(self, conversation_repository: ConversationRepository) -> None:
        self._conversation_repository = conversation_repository

    async def execute(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FavoriteConversationResult]:
        return await self._conversation_repository.find_favorites_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
