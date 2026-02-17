from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from raggae.domain.entities.document import Document
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.document_status import DocumentStatus


@dataclass
class DocumentDTO:
    """Data Transfer Object for Document."""

    id: UUID
    project_id: UUID
    file_name: str
    content_type: str
    file_size: int
    storage_key: str
    created_at: datetime
    processing_strategy: ChunkingStrategy | None
    status: DocumentStatus
    error_message: str | None
    language: str | None
    keywords: list[str] | None
    authors: list[str] | None
    document_date: date | None
    title: str | None

    @classmethod
    def from_entity(cls, document: Document) -> "DocumentDTO":
        return cls(
            id=document.id,
            project_id=document.project_id,
            file_name=document.file_name,
            content_type=document.content_type,
            file_size=document.file_size,
            storage_key=document.storage_key,
            created_at=document.created_at,
            processing_strategy=document.processing_strategy,
            status=document.status,
            error_message=document.error_message,
            language=document.language,
            keywords=document.keywords,
            authors=document.authors,
            document_date=document.document_date,
            title=document.title,
        )
