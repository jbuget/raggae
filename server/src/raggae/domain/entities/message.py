from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class Message:
    """Message domain entity."""

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime
    source_documents: list[dict[str, Any]] | None = None
    reliability_percent: int | None = None
    llm_prompt: str | None = None

    def __post_init__(self) -> None:
        if self.role not in {"user", "assistant", "system"}:
            raise ValueError("Message role must be one of: user, assistant, system")
