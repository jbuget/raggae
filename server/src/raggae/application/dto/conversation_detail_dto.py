from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.application.dto.message_dto import MessageDTO


@dataclass
class ConversationDetailDTO:
    id: UUID
    project_id: UUID
    user_id: UUID
    created_at: datetime
    title: str | None
    message_count: int
    last_message: MessageDTO | None
