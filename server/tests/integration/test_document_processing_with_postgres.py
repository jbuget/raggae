from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from raggae.application.use_cases.document.upload_document import UploadDocument
from raggae.domain.entities.project import Project
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_document_chunk_repository import (
    SQLAlchemyDocumentChunkRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_document_repository import (
    SQLAlchemyDocumentRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
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


class TestDocumentProcessingWithPostgres:
    @pytest.fixture
    async def session_factory(self) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(
            "postgresql+asyncpg://test:test@localhost:5433/raggae_test",
            echo=False,
        )
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
        except Exception as exc:  # pragma: no cover - environment dependent
            pytest.skip(f"PostgreSQL test database is not reachable: {exc}")

        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        yield factory

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    @pytest.mark.integration
    async def test_integration_sync_processing_persists_document_chunks(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()

        project_repository = SQLAlchemyProjectRepository(session_factory=session_factory)
        await project_repository.save(
            Project(
                id=project_id,
                user_id=user_id,
                name="Pg Project",
                description="",
                system_prompt="",
                is_published=False,
                created_at=datetime.now(UTC),
            )
        )
        document_repository = SQLAlchemyDocumentRepository(session_factory=session_factory)
        chunk_repository = SQLAlchemyDocumentChunkRepository(session_factory=session_factory)

        use_case = UploadDocument(
            document_repository=document_repository,
            project_repository=project_repository,
            file_storage_service=InMemoryFileStorageService(),
            max_file_size=104857600,
            processing_mode="sync",
            document_chunk_repository=chunk_repository,
            document_text_extractor=MultiFormatDocumentTextExtractor(),
            text_sanitizer_service=SimpleTextSanitizerService(),
            text_chunker_service=SimpleTextChunkerService(chunk_size=12, chunk_overlap=0),
            embedding_service=InMemoryEmbeddingService(dimension=16),
        )

        # When
        uploaded = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="source.txt",
            file_content=b"chunk me into several pieces",
            content_type="text/plain",
        )
        chunks = await chunk_repository.find_by_document_id(uploaded.id)

        # Then
        assert uploaded.project_id == project_id
        assert len(chunks) > 0
        assert all(chunk.document_id == uploaded.id for chunk in chunks)
