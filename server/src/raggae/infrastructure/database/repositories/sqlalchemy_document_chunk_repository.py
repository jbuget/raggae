from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.infrastructure.database.models.document_chunk_model import DocumentChunkModel


class SQLAlchemyDocumentChunkRepository:
    """PostgreSQL document chunk repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save_many(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        async with self._session_factory() as session:
            models = [
                DocumentChunkModel(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    embedding=chunk.embedding,
                    created_at=chunk.created_at,
                )
                for chunk in chunks
            ]
            session.add_all(models)
            await session.commit()

    async def delete_by_document_id(self, document_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
            )
            await session.commit()
