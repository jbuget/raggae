from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.document import Document


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
        )
