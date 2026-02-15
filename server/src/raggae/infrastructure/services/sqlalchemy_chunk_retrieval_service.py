from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


class SQLAlchemyChunkRetrievalService:
    """PostgreSQL chunk retrieval using hybrid vector and full-text scoring."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        vector_weight: float = 0.6,
        fulltext_weight: float = 0.4,
        candidate_multiplier: int = 5,
    ) -> None:
        self._session_factory = session_factory
        self._vector_weight = vector_weight
        self._fulltext_weight = fulltext_weight
        self._candidate_multiplier = max(1, candidate_multiplier)

    async def retrieve_chunks(
        self,
        project_id: UUID,
        query_text: str,
        query_embedding: list[float],
        limit: int,
        offset: int = 0,
        min_score: float = 0.0,
        strategy: str = "hybrid",
        metadata_filters: dict[str, object] | None = None,
    ) -> list[RetrievedChunkDTO]:
        if limit <= 0:
            return []

        vector_literal = _to_pgvector_literal(query_embedding)
        candidate_limit = limit * self._candidate_multiplier
        resolved_strategy = _resolve_strategy(strategy, query_text)
        vector_weight, fulltext_weight = self._weights_for_strategy(resolved_strategy)
        metadata_where, metadata_params = _build_metadata_filters(metadata_filters)
        sql = text(
            """
            WITH vector_search AS (
                SELECT
                    c.id AS chunk_id,
                    c.document_id AS document_id,
                    d.file_name AS document_file_name,
                    c.content AS content,
                    1 - (c.embedding <=> CAST(:query_embedding AS vector)) AS vector_score
                FROM document_chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE d.project_id = :project_id
                  {metadata_where}
                ORDER BY c.embedding <=> CAST(:query_embedding AS vector) ASC
                LIMIT :candidate_limit
            ),
            fulltext_search AS (
                SELECT
                    c.id AS chunk_id,
                    ts_rank_cd(
                        to_tsvector('simple', c.content),
                        plainto_tsquery('simple', :query_text)
                    ) AS fulltext_score
                FROM document_chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE d.project_id = :project_id
                  {metadata_where}
                  AND to_tsvector('simple', c.content) @@ plainto_tsquery('simple', :query_text)
                ORDER BY fulltext_score DESC
                LIMIT :candidate_limit
            ),
            combined AS (
                SELECT
                    v.chunk_id,
                    v.document_id,
                    v.document_file_name,
                    v.content,
                    v.vector_score,
                    COALESCE(f.fulltext_score, 0.0) AS fulltext_score
                FROM vector_search v
                LEFT JOIN fulltext_search f ON f.chunk_id = v.chunk_id
                UNION ALL
                SELECT
                    f.chunk_id,
                    c.document_id,
                    d.file_name AS document_file_name,
                    c.content,
                    0.0 AS vector_score,
                    f.fulltext_score
                FROM fulltext_search f
                JOIN document_chunks c ON c.id = f.chunk_id
                JOIN documents d ON d.id = c.document_id
                LEFT JOIN vector_search v ON v.chunk_id = f.chunk_id
                WHERE v.chunk_id IS NULL
            ),
            maxima AS (
                SELECT
                    MAX(vector_score) AS max_vector_score,
                    MAX(fulltext_score) AS max_fulltext_score
                FROM combined
            ),
            scored AS (
                SELECT
                    c.chunk_id,
                    c.document_id,
                    c.document_file_name,
                    c.content,
                    COALESCE(c.vector_score / NULLIF(m.max_vector_score, 0), 0.0)
                        AS normalized_vector_score,
                    COALESCE(c.fulltext_score / NULLIF(m.max_fulltext_score, 0), 0.0)
                        AS normalized_fulltext_score
                FROM combined c
                CROSS JOIN maxima m
            )
            SELECT
                chunk_id,
                document_id,
                document_file_name,
                content,
                normalized_vector_score AS vector_score,
                normalized_fulltext_score AS fulltext_score,
                (
                    (normalized_vector_score * :vector_weight)
                    + (normalized_fulltext_score * :fulltext_weight)
                ) AS final_score
            FROM scored
            WHERE (
                (normalized_vector_score * :vector_weight)
                + (normalized_fulltext_score * :fulltext_weight)
            ) >= :min_score
            ORDER BY final_score DESC
            LIMIT :limit
            OFFSET :offset
            """.replace("{metadata_where}", metadata_where)
        )

        async with self._session_factory() as session:
            rows = (
                await session.execute(
                    sql,
                    {
                        "project_id": project_id,
                        "query_text": query_text,
                        "query_embedding": vector_literal,
                        "candidate_limit": candidate_limit,
                        "vector_weight": vector_weight,
                        "fulltext_weight": fulltext_weight,
                        "limit": limit,
                        "offset": offset,
                        "min_score": min_score,
                        **metadata_params,
                    },
                )
            ).mappings()
            return [
                RetrievedChunkDTO(
                    chunk_id=row["chunk_id"],
                    document_id=row["document_id"],
                    content=row["content"],
                    score=float(row["final_score"]),
                    document_file_name=row["document_file_name"],
                    vector_score=float(row["vector_score"]),
                    fulltext_score=float(row["fulltext_score"]),
                )
                for row in rows
            ]

    def _weights_for_strategy(self, strategy: str) -> tuple[float, float]:
        if strategy == "vector":
            return 1.0, 0.0
        if strategy == "fulltext":
            return 0.0, 1.0
        return self._vector_weight, self._fulltext_weight


def _to_pgvector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(value) for value in values) + "]"


def _resolve_strategy(strategy: str, query_text: str) -> str:
    if strategy != "auto":
        return strategy
    has_quotes = '"' in query_text or "'" in query_text
    is_technical = any(character in query_text for character in ("_", "-")) or any(
        token.isupper() and len(token) > 1 for token in query_text.split()
    )
    is_short = len(query_text.split()) <= 3
    if has_quotes or (is_technical and is_short):
        return "fulltext"
    return "hybrid"


def _build_metadata_filters(
    filters: dict[str, object] | None,
) -> tuple[str, dict[str, object]]:
    if not filters:
        return "", {}
    clauses: list[str] = []
    params: dict[str, object] = {}

    if isinstance(filters.get("document_type"), list):
        clauses.append("(c.metadata_json->>'document_type') = ANY(:document_type)")
        params["document_type"] = filters["document_type"]
    if isinstance(filters.get("language"), str):
        clauses.append("(c.metadata_json->>'language') = :language")
        params["language"] = filters["language"]
    if isinstance(filters.get("source_type"), str):
        clauses.append("(c.metadata_json->>'source_type') = :source_type")
        params["source_type"] = filters["source_type"]
    if isinstance(filters.get("processing_strategy"), str):
        clauses.append("(c.metadata_json->>'processing_strategy') = :processing_strategy")
        params["processing_strategy"] = filters["processing_strategy"]
    if isinstance(filters.get("tags"), list):
        clauses.append("(c.metadata_json->'tags') ?| :tags")
        params["tags"] = filters["tags"]

    if not clauses:
        return "", {}
    return " AND " + " AND ".join(clauses), params
