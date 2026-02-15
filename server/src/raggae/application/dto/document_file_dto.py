from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DocumentFileDTO:
    document_id: UUID
    file_name: str
    content_type: str
    content: bytes
