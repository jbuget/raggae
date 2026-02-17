from uuid import UUID

from raggae.application.dto.document_dto import DocumentDTO
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.application.services.document_indexing_service import DocumentIndexingService
from raggae.domain.exceptions.document_exceptions import (
    DocumentExtractionError,
    DocumentNotFoundError,
    EmbeddingGenerationError,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.document_status import DocumentStatus


class ReindexDocument:
    """Use Case: Re-run the indexing pipeline on an existing document."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        project_repository: ProjectRepository,
        file_storage_service: FileStorageService,
        document_indexing_service: DocumentIndexingService,
    ) -> None:
        self._document_repository = document_repository
        self._project_repository = project_repository
        self._file_storage_service = file_storage_service
        self._document_indexing_service = document_indexing_service

    async def execute(
        self,
        project_id: UUID,
        document_id: UUID,
        user_id: UUID,
    ) -> DocumentDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        document = await self._document_repository.find_by_id(document_id)
        if document is None or document.project_id != project_id:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        try:
            if document.status != DocumentStatus.PROCESSING:
                document = document.transition_to(DocumentStatus.PROCESSING)
                await self._document_repository.save(document)

            file_content, _ = await self._file_storage_service.download_file(document.storage_key)
            document = await self._document_indexing_service.run_pipeline(document, file_content)
            document = document.transition_to(DocumentStatus.INDEXED)
        except (DocumentExtractionError, EmbeddingGenerationError, Exception) as exc:
            document = document.transition_to(DocumentStatus.ERROR, error_message=str(exc))

        await self._document_repository.save(document)
        return DocumentDTO.from_entity(document)
