from datetime import UTC, datetime
from uuid import uuid4

import pytest
from raggae.application.services.document_indexing_service import DocumentIndexingService
from raggae.application.use_cases.document.delete_document import DeleteDocument
from raggae.application.use_cases.document.upload_document import UploadDocument
from raggae.domain.entities.project import Project
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.database.repositories.in_memory_document_chunk_repository import (
    InMemoryDocumentChunkRepository,
)
from raggae.infrastructure.database.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.services.adaptive_text_chunker_service import (
    AdaptiveTextChunkerService,
)
from raggae.infrastructure.services.heading_section_text_chunker_service import (
    HeadingSectionTextChunkerService,
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
from raggae.infrastructure.services.paragraph_text_chunker_service import (
    ParagraphTextChunkerService,
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

        embedding_service = InMemoryEmbeddingService(dimension=16)
        document_indexing_service = DocumentIndexingService(
            document_chunk_repository=document_chunk_repository,
            document_text_extractor=MultiFormatDocumentTextExtractor(),
            text_sanitizer_service=SimpleTextSanitizerService(),
            document_structure_analyzer=HeuristicDocumentStructureAnalyzer(),
            text_chunker_service=SimpleTextChunkerService(chunk_size=10, chunk_overlap=0),
            embedding_service=embedding_service,
        )
        upload_use_case = UploadDocument(
            document_repository=document_repository,
            project_repository=project_repository,
            file_storage_service=file_storage_service,
            max_file_size=104857600,
            processing_mode="sync",
            document_chunk_repository=document_chunk_repository,
            document_indexing_service=document_indexing_service,
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

    @pytest.mark.integration
    async def test_integration_sync_processing_persists_heading_strategy(self) -> None:
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
        fixed_window_chunker = SimpleTextChunkerService(chunk_size=30, chunk_overlap=0)
        text_chunker_service = AdaptiveTextChunkerService(
            fixed_window_chunker=fixed_window_chunker,
            paragraph_chunker=ParagraphTextChunkerService(chunk_size=30),
            heading_section_chunker=HeadingSectionTextChunkerService(
                fallback_chunker=fixed_window_chunker
            ),
        )
        embedding_service = InMemoryEmbeddingService(dimension=16)
        document_indexing_service = DocumentIndexingService(
            document_chunk_repository=document_chunk_repository,
            document_text_extractor=MultiFormatDocumentTextExtractor(),
            text_sanitizer_service=SimpleTextSanitizerService(),
            document_structure_analyzer=HeuristicDocumentStructureAnalyzer(),
            text_chunker_service=text_chunker_service,
            embedding_service=embedding_service,
        )
        upload_use_case = UploadDocument(
            document_repository=document_repository,
            project_repository=project_repository,
            file_storage_service=file_storage_service,
            max_file_size=104857600,
            processing_mode="sync",
            document_chunk_repository=document_chunk_repository,
            document_indexing_service=document_indexing_service,
        )

        # When
        uploaded = await upload_use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="notes.md",
            file_content=b"# Title\n\n## Section 1\n\nBody content for section one.",
            content_type="text/markdown",
        )
        stored_document = await document_repository.find_by_id(uploaded.id)
        chunks = await document_chunk_repository.find_by_document_id(uploaded.id)

        # Then
        assert stored_document is not None
        assert stored_document.processing_strategy == ChunkingStrategy.HEADING_SECTION
        assert chunks
        assert chunks[0].metadata_json is not None
        assert chunks[0].metadata_json["chunker_backend"] == "native"

    @pytest.mark.integration
    async def test_integration_sync_processing_adds_context_window_for_paragraph_chunks(
        self,
    ) -> None:
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
        fixed_window_chunker = SimpleTextChunkerService(chunk_size=400, chunk_overlap=0)
        text_chunker_service = AdaptiveTextChunkerService(
            fixed_window_chunker=fixed_window_chunker,
            paragraph_chunker=ParagraphTextChunkerService(chunk_size=120),
            heading_section_chunker=HeadingSectionTextChunkerService(
                fallback_chunker=fixed_window_chunker
            ),
            context_window_size=6,
        )
        embedding_service = InMemoryEmbeddingService(dimension=16)
        document_indexing_service = DocumentIndexingService(
            document_chunk_repository=document_chunk_repository,
            document_text_extractor=MultiFormatDocumentTextExtractor(),
            text_sanitizer_service=SimpleTextSanitizerService(),
            document_structure_analyzer=HeuristicDocumentStructureAnalyzer(),
            text_chunker_service=text_chunker_service,
            embedding_service=embedding_service,
        )
        upload_use_case = UploadDocument(
            document_repository=document_repository,
            project_repository=project_repository,
            file_storage_service=file_storage_service,
            max_file_size=104857600,
            processing_mode="sync",
            document_chunk_repository=document_chunk_repository,
            document_indexing_service=document_indexing_service,
        )
        content = (
            b"This is paragraph one with enough text to keep narrative style and avoid "
            b"heading detection."
            b"\n\n"
            b"This is paragraph two with enough text to create a second paragraph chunk "
            b"candidate."
            b"\n\n"
            b"This is paragraph three with enough text to ensure multiple chunks exist."
        )

        # When
        uploaded = await upload_use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="narrative.txt",
            file_content=content,
            content_type="text/plain",
        )
        chunks = await document_chunk_repository.find_by_document_id(uploaded.id)

        # Then
        assert len(chunks) >= 2
        previous_tail = chunks[0].content[-6:].strip()
        assert previous_tail
        assert chunks[1].content.startswith(f"{previous_tail}\n\n")
