from dataclasses import dataclass, replace
from datetime import date, datetime
from uuid import UUID

from raggae.domain.exceptions.document_exceptions import (
    InvalidDocumentStatusTransitionError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.document_status import DocumentStatus

_ALLOWED_TRANSITIONS: dict[DocumentStatus, set[DocumentStatus]] = {
    DocumentStatus.UPLOADED: {DocumentStatus.PROCESSING},
    DocumentStatus.PROCESSING: {DocumentStatus.INDEXED, DocumentStatus.ERROR},
    DocumentStatus.INDEXED: {DocumentStatus.PROCESSING},
    DocumentStatus.ERROR: {DocumentStatus.PROCESSING},
}


@dataclass(frozen=True)
class Document:
    """Document domain entity."""

    id: UUID
    project_id: UUID
    file_name: str
    content_type: str
    file_size: int
    storage_key: str
    created_at: datetime
    processing_strategy: ChunkingStrategy | None = None
    status: DocumentStatus = DocumentStatus.UPLOADED
    error_message: str | None = None
    language: str | None = None
    keywords: list[str] | None = None
    authors: list[str] | None = None
    document_date: date | None = None
    title: str | None = None

    def transition_to(
        self,
        new_status: DocumentStatus,
        error_message: str | None = None,
    ) -> "Document":
        """Transition to a new status. Raises if the transition is not allowed."""
        allowed = _ALLOWED_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise InvalidDocumentStatusTransitionError(
                f"Cannot transition from '{self.status}' to '{new_status}'"
            )
        if new_status == DocumentStatus.ERROR:
            return replace(self, status=new_status, error_message=error_message)
        return replace(self, status=new_status, error_message=None)
