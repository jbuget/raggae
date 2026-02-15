from uuid import UUID

from pydantic import BaseModel, Field


class QueryProjectRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class RetrievedChunkResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_file_name: str | None = None
    content: str
    score: float


class QueryProjectResponse(BaseModel):
    project_id: UUID
    query: str
    chunks: list[RetrievedChunkResponse]
