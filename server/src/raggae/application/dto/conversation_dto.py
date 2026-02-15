from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.conversation import Conversation


@dataclass
class ConversationDTO:
    id: UUID
    project_id: UUID
    user_id: UUID
    created_at: datetime
    title: str | None

    @classmethod
    def from_entity(cls, conversation: Conversation) -> "ConversationDTO":
        return cls(
            id=conversation.id,
            project_id=conversation.project_id,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            title=conversation.title,
        )
