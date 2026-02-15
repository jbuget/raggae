from dataclasses import dataclass
from uuid import UUID

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


@dataclass
class ChatMessageResponseDTO:
    project_id: UUID
    conversation_id: UUID
    message: str
    answer: str
    chunks: list[RetrievedChunkDTO]
    retrieval_strategy_used: str = "hybrid"
    retrieval_execution_time_ms: float = 0.0
    history_messages_used: int = 0
    chunks_used: int = 0
