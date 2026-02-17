from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.document_status import DocumentStatus


class DocumentResponse(BaseModel):
    id: UUID
    project_id: UUID
    file_name: str
    content_type: str
    file_size: int
    created_at: datetime
    processing_strategy: ChunkingStrategy | None
    status: DocumentStatus
    error_message: str | None = None
    language: str | None = None
    keywords: list[str] | None = None
    authors: list[str] | None = None
    document_date: date | None = None
    title: str | None = None


class UploadDocumentsCreatedResponse(BaseModel):
    original_filename: str
    stored_filename: str
    document_id: UUID


class UploadDocumentsErrorResponse(BaseModel):
    filename: str
    code: str
    message: str


class UploadDocumentsResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    created: list[UploadDocumentsCreatedResponse]
    errors: list[UploadDocumentsErrorResponse]


class DocumentChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    created_at: datetime
    metadata_json: dict[str, Any] | None


class DocumentChunksResponse(BaseModel):
    document_id: UUID
    processing_strategy: ChunkingStrategy | None
    chunks: list[DocumentChunkResponse]
