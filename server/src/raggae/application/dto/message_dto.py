from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from raggae.domain.entities.message import Message


@dataclass
class MessageDTO:
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime
    source_documents: list[dict[str, Any]] | None

    @classmethod
    def from_entity(cls, message: Message) -> "MessageDTO":
        return cls(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
            source_documents=message.source_documents,
        )
