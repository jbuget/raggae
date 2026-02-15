from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.document_dto import DocumentDTO
from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.document_text_extractor import (
    DocumentTextExtractor,
)
from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.application.interfaces.services.text_chunker_service import TextChunkerService
from raggae.application.interfaces.services.text_sanitizer_service import (
    TextSanitizerService,
)
from raggae.domain.entities.document import Document
from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.domain.exceptions.document_exceptions import (
    DocumentTooLargeError,
    InvalidDocumentTypeError,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError

ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "doc", "docx"}


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
        document_text_extractor: DocumentTextExtractor | None = None,
        text_sanitizer_service: TextSanitizerService | None = None,
        text_chunker_service: TextChunkerService | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self._document_repository = document_repository
        self._project_repository = project_repository
        self._file_storage_service = file_storage_service
        self._max_file_size = max_file_size
        self._processing_mode = processing_mode
        self._document_chunk_repository = document_chunk_repository
        self._document_text_extractor = document_text_extractor
        self._text_sanitizer_service = text_sanitizer_service
        self._text_chunker_service = text_chunker_service
        self._embedding_service = embedding_service

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        file_name: str,
        file_content: bytes,
        content_type: str,
    ) -> DocumentDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

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
        )
        await self._document_repository.save(document)

        if (
            self._processing_mode == "sync"
            and self._document_chunk_repository is not None
            and self._document_text_extractor is not None
            and self._text_sanitizer_service is not None
            and self._text_chunker_service is not None
            and self._embedding_service is not None
        ):
            extracted_text = await self._document_text_extractor.extract_text(
                file_name=file_name,
                content=file_content,
                content_type=content_type,
            )
            sanitized_text = await self._text_sanitizer_service.sanitize_text(extracted_text)
            chunks = await self._text_chunker_service.chunk_text(sanitized_text)
            if chunks:
                embeddings = await self._embedding_service.embed_texts(chunks)
                document_chunks = [
                    DocumentChunk(
                        id=uuid4(),
                        document_id=document.id,
                        chunk_index=index,
                        content=chunk_text,
                        embedding=embeddings[index],
                        created_at=datetime.now(UTC),
                    )
                    for index, chunk_text in enumerate(chunks)
                ]
                await self._document_chunk_repository.save_many(document_chunks)

        return DocumentDTO.from_entity(document)
