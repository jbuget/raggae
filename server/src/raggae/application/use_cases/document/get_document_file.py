from uuid import UUID

from raggae.application.dto.document_file_dto import DocumentFileDTO
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.domain.exceptions.document_exceptions import DocumentNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class GetDocumentFile:
    """Use Case: Retrieve original document binary content from storage."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        project_repository: ProjectRepository,
        file_storage_service: FileStorageService,
    ) -> None:
        self._document_repository = document_repository
        self._project_repository = project_repository
        self._file_storage_service = file_storage_service

    async def execute(
        self,
        project_id: UUID,
        document_id: UUID,
        user_id: UUID,
    ) -> DocumentFileDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        document = await self._document_repository.find_by_id(document_id)
        if document is None or document.project_id != project_id:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        content, content_type = await self._file_storage_service.download_file(document.storage_key)
        return DocumentFileDTO(
            document_id=document.id,
            file_name=document.file_name,
            content_type=content_type or document.content_type,
            content=content,
        )
