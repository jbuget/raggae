from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.document_dto import DocumentDTO
from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.application.services.document_indexing_service import DocumentIndexingService
from raggae.domain.entities.document import Document
from raggae.domain.exceptions.document_exceptions import (
    DocumentExtractionError,
    DocumentTooLargeError,
    EmbeddingGenerationError,
    InvalidDocumentTypeError,
    ProjectDocumentLimitReachedError,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.document_status import DocumentStatus

ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "docx"}


@dataclass(frozen=True)
class UploadDocumentItem:
    file_name: str
    file_content: bytes
    content_type: str


@dataclass(frozen=True)
class UploadDocumentsCreatedItem:
    original_filename: str
    stored_filename: str
    document_id: UUID


@dataclass(frozen=True)
class UploadDocumentsErrorItem:
    filename: str
    code: str
    message: str


@dataclass(frozen=True)
class UploadDocumentsResult:
    total: int
    succeeded: int
    failed: int
    created: list[UploadDocumentsCreatedItem]
    errors: list[UploadDocumentsErrorItem]


class UploadDocument:
    """Use Case: Upload and attach a document to a project."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        project_repository: ProjectRepository,
        file_storage_service: FileStorageService,
        max_file_size: int,
        processing_mode: str = "off",
        document_chunk_repository: DocumentChunkRepository | None = None,
        document_indexing_service: DocumentIndexingService | None = None,
        max_documents_per_project: int | None = None,
    ) -> None:
        self._document_repository = document_repository
        self._project_repository = project_repository
        self._file_storage_service = file_storage_service
        self._max_file_size = max_file_size
        self._processing_mode = processing_mode
        if self._processing_mode not in {"off", "sync", "async"}:
            raise ValueError(f"Unsupported processing mode: {self._processing_mode}")
        self._document_chunk_repository = document_chunk_repository
        self._document_indexing_service = document_indexing_service
        self._max_documents_per_project = max_documents_per_project

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        file_name: str,
        file_content: bytes,
        content_type: str,
    ) -> DocumentDTO:
        await self._assert_project_owner(project_id=project_id, user_id=user_id)
        await self._assert_document_quota(project_id=project_id)
        return await self._execute_single(
            project_id=project_id,
            file_name=file_name,
            file_content=file_content,
            content_type=content_type,
        )

    async def execute_many(
        self,
        project_id: UUID,
        user_id: UUID,
        files: list[UploadDocumentItem],
    ) -> UploadDocumentsResult:
        await self._assert_project_owner(project_id=project_id, user_id=user_id)
        existing_documents = await self._document_repository.find_by_project_id(project_id)
        indexed_by_name = {
            doc.file_name.lower()
            for doc in existing_documents
            if doc.processing_strategy is not None
        }
        existing_names = {doc.file_name.lower() for doc in existing_documents}
        request_names: set[str] = set()
        created: list[UploadDocumentsCreatedItem] = []
        errors: list[UploadDocumentsErrorItem] = []

        for item in files:
            request_name = item.file_name.lower()
            if request_name in request_names:
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="DUPLICATE_IN_REQUEST",
                        message="Duplicate filename in request.",
                    )
                )
                continue
            request_names.add(request_name)
            if request_name in indexed_by_name:
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="ALREADY_INDEXED",
                        message="Document already exists and is already indexed for this project.",
                    )
                )
                continue
            stored_filename = self._resolve_unique_filename(item.file_name, existing_names)
            try:
                document_dto = await self._execute_single(
                    project_id=project_id,
                    file_name=stored_filename,
                    file_content=item.file_content,
                    content_type=item.content_type,
                )
            except InvalidDocumentTypeError as exc:
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="INVALID_FILE_TYPE",
                        message=str(exc),
                    )
                )
                continue
            except DocumentTooLargeError:
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="FILE_TOO_LARGE",
                        message="Document exceeds maximum allowed size",
                    )
                )
                continue
            except (DocumentExtractionError, EmbeddingGenerationError) as exc:
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="PROCESSING_FAILED",
                        message=str(exc),
                    )
                )
                continue

            existing_names.add(stored_filename.lower())
            created.append(
                UploadDocumentsCreatedItem(
                    original_filename=item.file_name,
                    stored_filename=stored_filename,
                    document_id=document_dto.id,
                )
            )

        return UploadDocumentsResult(
            total=len(files),
            succeeded=len(created),
            failed=len(errors),
            created=created,
            errors=errors,
        )

    async def _assert_project_owner(self, project_id: UUID, user_id: UUID) -> None:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

    async def _assert_document_quota(self, project_id: UUID) -> None:
        if self._max_documents_per_project is None:
            return
        existing = await self._document_repository.find_by_project_id(project_id)
        if len(existing) >= self._max_documents_per_project:
            raise ProjectDocumentLimitReachedError(
                f"Project {project_id} has reached the maximum of "
                f"{self._max_documents_per_project} documents"
            )

    async def _execute_single(
        self,
        project_id: UUID,
        file_name: str,
        file_content: bytes,
        content_type: str,
    ) -> DocumentDTO:
        extension = file_name.rsplit(".", maxsplit=1)[-1].lower() if "." in file_name else ""
        if extension not in ALLOWED_EXTENSIONS:
            raise InvalidDocumentTypeError(f"Unsupported document type: {extension}")

        file_size = len(file_content)
        if file_size > self._max_file_size:
            raise DocumentTooLargeError("Document exceeds maximum allowed size")

        document_id = uuid4()
        storage_key = f"projects/{project_id}/documents/{document_id}-{file_name}"
        await self._file_storage_service.upload_file(storage_key, file_content, content_type)

        document = Document(
            id=document_id,
            project_id=project_id,
            file_name=file_name,
            content_type=content_type,
            file_size=file_size,
            storage_key=storage_key,
            created_at=datetime.now(UTC),
            status=DocumentStatus.UPLOADED,
        )
        await self._document_repository.save(document)
        try:
            if self._processing_mode == "sync" and self._document_indexing_service is not None:
                document = document.transition_to(DocumentStatus.PROCESSING)
                await self._document_repository.save(document)
                document = await self._document_indexing_service.run_pipeline(
                    document, file_content
                )
                document = document.transition_to(DocumentStatus.INDEXED)
                await self._document_repository.save(document)
        except (DocumentExtractionError, EmbeddingGenerationError) as exc:
            document = document.transition_to(DocumentStatus.ERROR, error_message=str(exc))
            await self._document_repository.save(document)
            await self._cleanup_failed_document(
                document_id=document.id, storage_key=document.storage_key
            )
            raise

        return DocumentDTO.from_entity(document)

    async def _cleanup_failed_document(self, document_id: UUID, storage_key: str) -> None:
        await self._file_storage_service.delete_file(storage_key)
        if self._document_chunk_repository is not None:
            await self._document_chunk_repository.delete_by_document_id(document_id)
        await self._document_repository.delete(document_id)

    def _resolve_unique_filename(self, file_name: str, existing_names: set[str]) -> str:
        normalized = file_name.lower()
        if normalized not in existing_names:
            return file_name

        name, extension = file_name.rsplit(".", maxsplit=1) if "." in file_name else (file_name, "")
        index = 1
        while True:
            if extension:
                candidate = f"{name}-copie-{index}.{extension}"
            else:
                candidate = f"{name}-copie-{index}"
            if candidate.lower() not in existing_names:
                return candidate
            index += 1
