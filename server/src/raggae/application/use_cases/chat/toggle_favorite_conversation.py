from uuid import UUID

from raggae.application.interfaces.repositories.conversation_repository import ConversationRepository
from raggae.domain.entities.conversation import Conversation
from raggae.domain.exceptions.conversation_exceptions import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
)


class ToggleFavoriteConversation:
    """Use Case: Toggle the favorite status of a conversation owned by the user."""

    def __init__(self, conversation_repository: ConversationRepository) -> None:
        self._conversation_repository = conversation_repository

    async def execute(self, conversation_id: UUID, user_id: UUID) -> Conversation:
        conversation = await self._conversation_repository.find_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
        if conversation.user_id != user_id:
            raise ConversationAccessDeniedError(f"User {user_id} does not own conversation {conversation_id}")
        return await self._conversation_repository.toggle_favorite(conversation_id)
