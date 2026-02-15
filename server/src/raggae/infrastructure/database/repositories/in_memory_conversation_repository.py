from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.domain.entities.conversation import Conversation


class InMemoryConversationRepository:
    """In-memory conversation repository for testing."""

    def __init__(self) -> None:
        self._conversations: dict[UUID, Conversation] = {}

    async def create(self, project_id: UUID, user_id: UUID) -> Conversation:
        created = Conversation(
            id=uuid4(),
            project_id=project_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
            title="New conversation",
        )
        self._conversations[created.id] = created
        return created

    async def get_or_create(self, project_id: UUID, user_id: UUID) -> Conversation:
        for conversation in self._conversations.values():
            if conversation.project_id == project_id and conversation.user_id == user_id:
                return conversation

        return await self.create(project_id=project_id, user_id=user_id)

    async def find_by_id(self, conversation_id: UUID) -> Conversation | None:
        return self._conversations.get(conversation_id)

    async def find_by_project_and_user(
        self,
        project_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        conversations = [
            conversation
            for conversation in self._conversations.values()
            if conversation.project_id == project_id and conversation.user_id == user_id
        ]
        conversations.sort(key=lambda item: item.created_at, reverse=True)
        return conversations[offset : offset + limit]

    async def delete(self, conversation_id: UUID) -> None:
        self._conversations.pop(conversation_id, None)

    async def update_title(self, conversation_id: UUID, title: str) -> None:
        conversation = self._conversations.get(conversation_id)
        if conversation is None:
            return
        self._conversations[conversation_id] = replace(conversation, title=title)
