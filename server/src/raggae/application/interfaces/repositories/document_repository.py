from typing import Protocol
from uuid import UUID

from raggae.domain.entities.document import Document


class DocumentRepository(Protocol):
    """Interface for document persistence."""

    async def save(self, document: Document) -> None: ...

    async def find_by_id(self, document_id: UUID) -> Document | None: ...

    async def find_by_project_id(self, project_id: UUID) -> list[Document]: ...

    async def delete(self, document_id: UUID) -> None: ...
