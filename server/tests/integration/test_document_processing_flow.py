from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.document.delete_document import DeleteDocument
from raggae.application.use_cases.document.upload_document import UploadDocument
from raggae.domain.entities.project import Project
from raggae.infrastructure.database.repositories.in_memory_document_chunk_repository import (
    InMemoryDocumentChunkRepository,
)
from raggae.infrastructure.database.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.services.heuristic_document_structure_analyzer import (
    HeuristicDocumentStructureAnalyzer,
)
from raggae.infrastructure.services.in_memory_embedding_service import (
    InMemoryEmbeddingService,
)
from raggae.infrastructure.services.in_memory_file_storage_service import (
    InMemoryFileStorageService,
)
from raggae.infrastructure.services.multiformat_document_text_extractor import (
    MultiFormatDocumentTextExtractor,
)
from raggae.infrastructure.services.simple_text_chunker_service import (
    SimpleTextChunkerService,
)
from raggae.infrastructure.services.simple_text_sanitizer_service import (
    SimpleTextSanitizerService,
)


class TestDocumentProcessingFlow:
    @pytest.mark.integration
    async def test_integration_upload_sync_then_delete_cleans_chunks(self) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        project_repository = InMemoryProjectRepository()
        await project_repository.save(
            Project(
                id=project_id,
                user_id=user_id,
                name="Integration Project",
                description="",
                system_prompt="",
                is_published=False,
                created_at=datetime.now(UTC),
            )
        )

        document_repository = InMemoryDocumentRepository()
        document_chunk_repository = InMemoryDocumentChunkRepository()
        file_storage_service = InMemoryFileStorageService()

        upload_use_case = UploadDocument(
            document_repository=document_repository,
            project_repository=project_repository,
            file_storage_service=file_storage_service,
            max_file_size=104857600,
            processing_mode="sync",
            document_chunk_repository=document_chunk_repository,
            document_text_extractor=MultiFormatDocumentTextExtractor(),
            text_sanitizer_service=SimpleTextSanitizerService(),
            document_structure_analyzer=HeuristicDocumentStructureAnalyzer(),
            text_chunker_service=SimpleTextChunkerService(chunk_size=10, chunk_overlap=0),
            embedding_service=InMemoryEmbeddingService(dimension=16),
        )
        delete_use_case = DeleteDocument(
            document_repository=document_repository,
            document_chunk_repository=document_chunk_repository,
            project_repository=project_repository,
            file_storage_service=file_storage_service,
        )

        # When
        uploaded = await upload_use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="notes.txt",
            file_content=b"hello world from raggae integration flow",
            content_type="text/plain",
        )
        chunks_after_upload = await document_chunk_repository.find_by_document_id(uploaded.id)
        await delete_use_case.execute(
            project_id=project_id,
            document_id=uploaded.id,
            user_id=user_id,
        )
        chunks_after_delete = await document_chunk_repository.find_by_document_id(uploaded.id)

        # Then
        assert uploaded.project_id == project_id
        assert len(chunks_after_upload) > 0
        assert chunks_after_delete == []
