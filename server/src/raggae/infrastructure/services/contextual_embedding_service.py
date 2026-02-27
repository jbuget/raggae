"""Contextual embedding wrapper that adds prefix context before embedding.

This improves retrieval by making query/document embeddings more discriminative.
"""

from __future__ import annotations

from raggae.application.interfaces.services.embedding_service import EmbeddingService


class ContextualEmbeddingService:
    """Wraps any EmbeddingService to prepend a task-specific prefix.

    Following the pattern of modern embedding models (e.g. E5, BGE):
    - Documents are prefixed with ``document_prefix``
    - Queries are prefixed with ``query_prefix``
    """

    def __init__(
        self,
        delegate: EmbeddingService,
        document_prefix: str = "search_document: ",
        query_prefix: str = "search_query: ",
    ) -> None:
        self._delegate = delegate
        self._document_prefix = document_prefix
        self._query_prefix = query_prefix

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed texts with the document prefix."""
        prefixed = [f"{self._document_prefix}{t}" for t in texts]
        return await self._delegate.embed_texts(prefixed)

    async def embed_query(self, query: str) -> list[float]:
        """Embed a single query with the query prefix."""
        prefixed = f"{self._query_prefix}{query}"
        results = await self._delegate.embed_texts([prefixed])
        return results[0]

