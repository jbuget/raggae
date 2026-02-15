from dataclasses import dataclass, field
from uuid import UUID

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


@dataclass
class ChatStreamToken:
    token: str


@dataclass
class ChatStreamDone:
    conversation_id: UUID
    answer: str
    chunks: list[RetrievedChunkDTO] = field(default_factory=list)
    retrieval_strategy_used: str = "hybrid"
    retrieval_execution_time_ms: float = 0.0
    history_messages_used: int = 0
    chunks_used: int = 0


ChatStreamEvent = ChatStreamToken | ChatStreamDone
