from uuid import UUID

from raggae.domain.entities.document import Document


class InMemoryDocumentRepository:
    """In-memory document repository for testing."""

    def __init__(self) -> None:
        self._documents: dict[UUID, Document] = {}

    async def save(self, document: Document) -> None:
        self._documents[document.id] = document

    async def find_by_id(self, document_id: UUID) -> Document | None:
        return self._documents.get(document_id)

    async def find_by_project_id(self, project_id: UUID) -> list[Document]:
        return [doc for doc in self._documents.values() if doc.project_id == project_id]

    async def delete(self, document_id: UUID) -> None:
        self._documents.pop(document_id, None)
