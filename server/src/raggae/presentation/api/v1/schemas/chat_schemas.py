from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from raggae.presentation.api.v1.schemas.query_schemas import RetrievedChunkResponse


class RetrievalFiltersRequest(BaseModel):
    document_type: list[str] | None = None
    language: str | None = None
    source_type: str | None = None
    processing_strategy: str | None = None
    tags: list[str] | None = None


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    limit: int | None = Field(default=None, ge=1, le=40)
    offset: int = Field(default=0, ge=0)
    conversation_id: UUID | None = None
    start_new_conversation: bool = False
    retrieval_strategy: Literal["vector", "fulltext", "hybrid", "auto"] | None = None
    retrieval_filters: RetrievalFiltersRequest | None = None


class SendMessageResponse(BaseModel):
    project_id: UUID
    conversation_id: UUID
    message: str
    answer: str
    chunks: list[RetrievedChunkResponse]
    retrieval_strategy_used: Literal["vector", "fulltext", "hybrid"]
    retrieval_execution_time_ms: float
    history_messages_used: int
    chunks_used: int


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    source_documents: list[dict[str, object]] | None = None
    reliability_percent: int | None = None
    created_at: datetime


class ConversationResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    created_at: datetime
    title: str | None


class ConversationDetailResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    created_at: datetime
    title: str | None
    message_count: int
    last_message: MessageResponse | None


class UpdateConversationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
