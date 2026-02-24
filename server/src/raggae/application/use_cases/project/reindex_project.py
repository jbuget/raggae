from uuid import UUID

from raggae.application.dto.reindex_project_result_dto import ReindexProjectResultDTO
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.application.interfaces.services.project_embedding_service_resolver import (
    ProjectEmbeddingServiceResolver,
)
from raggae.application.services.document_indexing_service import DocumentIndexingService
from raggae.domain.exceptions.document_exceptions import (
    DocumentExtractionError,
    EmbeddingGenerationError,
)
from raggae.domain.exceptions.project_exceptions import (
    ProjectNotFoundError,
    ProjectReindexInProgressError,
)
from raggae.domain.value_objects.document_status import DocumentStatus


class ReindexProject:
    """Use Case: Reindex all documents of a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        document_repository: DocumentRepository,
        file_storage_service: FileStorageService,
        document_indexing_service: DocumentIndexingService,
        project_embedding_service_resolver: ProjectEmbeddingServiceResolver | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._document_repository = document_repository
        self._file_storage_service = file_storage_service
        self._document_indexing_service = document_indexing_service
        self._project_embedding_service_resolver = project_embedding_service_resolver

    async def execute(self, project_id: UUID, user_id: UUID) -> ReindexProjectResultDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        if project.is_reindexing():
            raise ProjectReindexInProgressError(f"Project {project_id} is already reindexing")

        documents = await self._document_repository.find_by_project_id(project_id)
        project = project.start_reindex(total_documents=len(documents))
        await self._project_repository.save(project)

        indexed_documents = 0
        failed_documents = 0
        for document in documents:
            try:
                if document.status != DocumentStatus.PROCESSING:
                    document = document.transition_to(DocumentStatus.PROCESSING)
                    await self._document_repository.save(document)

                file_content, _ = await self._file_storage_service.download_file(
                    document.storage_key
                )
                embedding_service = (
                    self._project_embedding_service_resolver.resolve(project)
                    if self._project_embedding_service_resolver is not None
                    else None
                )
                document = await self._document_indexing_service.run_pipeline(
                    document=document,
                    project=project,
                    file_content=file_content,
                    embedding_service=embedding_service,
                )
                document = document.transition_to(DocumentStatus.INDEXED)
                indexed_documents += 1
            except (DocumentExtractionError, EmbeddingGenerationError, FileNotFoundError) as exc:
                document = document.transition_to(DocumentStatus.ERROR, error_message=str(exc))
                failed_documents += 1

            await self._document_repository.save(document)
            project = project.advance_reindex()
            await self._project_repository.save(project)

        project = project.finish_reindex()
        await self._project_repository.save(project)

        return ReindexProjectResultDTO(
            project_id=project_id,
            total_documents=len(documents),
            indexed_documents=indexed_documents,
            failed_documents=failed_documents,
        )
