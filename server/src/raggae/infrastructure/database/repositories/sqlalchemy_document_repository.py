from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.document import Document
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.document_status import DocumentStatus
from raggae.infrastructure.database.models.document_model import DocumentModel


def _to_entity(model: DocumentModel) -> Document:
    return Document(
        id=model.id,
        project_id=model.project_id,
        file_name=model.file_name,
        content_type=model.content_type,
        file_size=model.file_size,
        storage_key=model.storage_key,
        created_at=model.created_at,
        processing_strategy=(
            ChunkingStrategy(model.processing_strategy)
            if model.processing_strategy is not None
            else None
        ),
        status=DocumentStatus(model.status),
        error_message=model.error_message,
        language=model.language,
        keywords=model.keywords,
        authors=model.authors,
        document_date=model.document_date,
        title=model.title,
    )


class SQLAlchemyDocumentRepository:
    """PostgreSQL document repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, document: Document) -> None:
        async with self._session_factory() as session:
            model = await session.get(DocumentModel, document.id)
            if model is None:
                model = DocumentModel(
                    id=document.id,
                    project_id=document.project_id,
                    file_name=document.file_name,
                    content_type=document.content_type,
                    file_size=document.file_size,
                    storage_key=document.storage_key,
                    processing_strategy=(
                        document.processing_strategy.value
                        if document.processing_strategy is not None
                        else None
                    ),
                    created_at=document.created_at,
                    status=document.status.value,
                    error_message=document.error_message,
                    language=document.language,
                    keywords=document.keywords,
                    authors=document.authors,
                    document_date=document.document_date,
                    title=document.title,
                )
                session.add(model)
            else:
                model.project_id = document.project_id
                model.file_name = document.file_name
                model.content_type = document.content_type
                model.file_size = document.file_size
                model.storage_key = document.storage_key
                model.processing_strategy = (
                    document.processing_strategy.value
                    if document.processing_strategy is not None
                    else None
                )
                model.status = document.status.value
                model.error_message = document.error_message
                model.language = document.language
                model.keywords = document.keywords
                model.authors = document.authors
                model.document_date = document.document_date
                model.title = document.title
            await session.commit()

    async def find_by_id(self, document_id: UUID) -> Document | None:
        async with self._session_factory() as session:
            model = await session.get(DocumentModel, document_id)
            if model is None:
                return None
            return _to_entity(model)

    async def find_by_project_id(self, project_id: UUID) -> list[Document]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentModel).where(DocumentModel.project_id == project_id)
            )
            models = result.scalars().all()
            return [_to_entity(model) for model in models]

    async def delete(self, document_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(delete(DocumentModel).where(DocumentModel.id == document_id))
            await session.commit()
