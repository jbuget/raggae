from dataclasses import replace

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


class InMemoryRerankerService:
    """Fake reranker for tests: scores by word overlap between query and chunk content."""

    async def rerank(
        self, query: str, chunks: list[RetrievedChunkDTO], top_k: int
    ) -> list[RetrievedChunkDTO]:
        query_words = set(query.lower().split())
        scored = []
        for chunk in chunks:
            chunk_words = set(chunk.content.lower().split())
            overlap = len(query_words & chunk_words)
            total = len(query_words | chunk_words) or 1
            score = overlap / total
            scored.append(replace(chunk, score=score))
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:top_k]
