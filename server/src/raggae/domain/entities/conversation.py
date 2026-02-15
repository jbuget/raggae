from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Conversation:
    """Conversation domain entity."""

    id: UUID
    project_id: UUID
    user_id: UUID
    created_at: datetime
    title: str | None = None
