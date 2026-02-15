from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


class SQLAlchemyChunkRetrievalService:
    """PostgreSQL chunk retrieval using pgvector cosine distance."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def retrieve_chunks(
        self,
        project_id: UUID,
        query_embedding: list[float],
        limit: int,
        min_score: float = 0.0,
    ) -> list[RetrievedChunkDTO]:
        if limit <= 0:
            return []

        vector_literal = _to_pgvector_literal(query_embedding)
        sql = text(
            """
            SELECT
                c.id AS chunk_id,
                c.document_id AS document_id,
                d.file_name AS document_file_name,
                c.content AS content,
                1 - (c.embedding <=> CAST(:query_embedding AS vector)) AS score
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.project_id = :project_id
              AND (1 - (c.embedding <=> CAST(:query_embedding AS vector))) >= :min_score
            ORDER BY c.embedding <=> CAST(:query_embedding AS vector) ASC
            LIMIT :limit
            """
        )

        async with self._session_factory() as session:
            rows = (
                await session.execute(
                    sql,
                    {
                        "project_id": project_id,
                        "query_embedding": vector_literal,
                        "limit": limit,
                        "min_score": min_score,
                    },
                )
            ).mappings()
            return [
                RetrievedChunkDTO(
                    chunk_id=row["chunk_id"],
                    document_id=row["document_id"],
                    content=row["content"],
                    score=float(row["score"]),
                    document_file_name=row["document_file_name"],
                )
                for row in rows
            ]


def _to_pgvector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(value) for value in values) + "]"
