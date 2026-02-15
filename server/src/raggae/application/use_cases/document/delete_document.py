from uuid import UUID

from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.domain.exceptions.document_exceptions import DocumentNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class DeleteDocument:
    """Use Case: Delete a document attached to a project."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        document_chunk_repository: DocumentChunkRepository,
        project_repository: ProjectRepository,
        file_storage_service: FileStorageService,
    ) -> None:
        self._document_repository = document_repository
        self._document_chunk_repository = document_chunk_repository
        self._project_repository = project_repository
        self._file_storage_service = file_storage_service

    async def execute(self, project_id: UUID, document_id: UUID, user_id: UUID) -> None:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        document = await self._document_repository.find_by_id(document_id)
        if document is None or document.project_id != project_id:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        await self._file_storage_service.delete_file(document.storage_key)
        await self._document_chunk_repository.delete_by_document_id(document.id)
        await self._document_repository.delete(document_id)
