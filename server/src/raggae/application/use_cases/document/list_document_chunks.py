from uuid import UUID

from raggae.application.dto.document_chunk_dto import DocumentChunkDTO
from raggae.application.dto.document_chunks_dto import DocumentChunksDTO
from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.exceptions.document_exceptions import DocumentNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class ListDocumentChunks:
    """Use Case: List chunks attached to a document."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        document_chunk_repository: DocumentChunkRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._document_repository = document_repository
        self._document_chunk_repository = document_chunk_repository
        self._project_repository = project_repository

    async def execute(
        self,
        project_id: UUID,
        document_id: UUID,
        user_id: UUID,
    ) -> DocumentChunksDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        document = await self._document_repository.find_by_id(document_id)
        if document is None or document.project_id != project_id:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        chunks = await self._document_chunk_repository.find_by_document_id(document_id)
        return DocumentChunksDTO(
            document_id=document.id,
            processing_strategy=document.processing_strategy,
            chunks=[DocumentChunkDTO.from_entity(chunk) for chunk in chunks],
        )
