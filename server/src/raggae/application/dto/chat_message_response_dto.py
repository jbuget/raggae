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
