from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from raggae.presentation.api.v1.schemas.query_schemas import RetrievedChunkResponse


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    conversation_id: UUID | None = None


class SendMessageResponse(BaseModel):
    project_id: UUID
    conversation_id: UUID
    message: str
    answer: str
    chunks: list[RetrievedChunkResponse]


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    source_documents: list[dict[str, str]] | None = None
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
