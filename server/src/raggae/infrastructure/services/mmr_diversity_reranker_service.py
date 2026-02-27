"""Maximal Marginal Relevance (MMR) diversity reranker.

Re-ranks retrieved chunks to balance relevance and diversity,
reducing redundancy in the context window.
"""

from __future__ import annotations

from dataclasses import replace
from math import sqrt

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


class MmrDiversityRerankerService:
    """Reranker using MMR to promote diversity among selected chunks.

    MMR = λ * relevance(query, chunk) - (1-λ) * max(sim(chunk, selected_chunks))

    With λ=0.85 we prioritise relevance while still reducing redundancy.
    """

    def __init__(
        self,
        lambda_param: float = 0.85,
    ) -> None:
        self._lambda = max(0.0, min(1.0, lambda_param))

    async def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunkDTO],
        top_k: int,
        chunk_embeddings: list[list[float]] | None = None,
        query_embedding: list[float] | None = None,
    ) -> list[RetrievedChunkDTO]:
        """Rerank chunks using MMR for diversity.

        If chunk_embeddings are not provided, falls back to lexical MMR.
        """
        if not chunks:
            return []
        if top_k <= 0:
            return []

        if chunk_embeddings is not None and query_embedding is not None:
            return self._mmr_with_embeddings(
                chunks, chunk_embeddings, query_embedding, top_k
            )
        return self._mmr_lexical(chunks, query, top_k)

    def _mmr_with_embeddings(
        self,
        chunks: list[RetrievedChunkDTO],
        embeddings: list[list[float]],
        query_embedding: list[float],
        top_k: int,
    ) -> list[RetrievedChunkDTO]:
        selected: list[int] = []
        remaining = list(range(len(chunks)))

        # Use the original hybrid score as the relevance signal when available,
        # falling back to cosine similarity with the query.
        relevance: list[float] = []
        for i in range(len(chunks)):
            if chunks[i].score > 0:
                relevance.append(chunks[i].score)
            else:
                relevance.append(_cosine_sim(query_embedding, embeddings[i]))

        # Normalise relevance to [0, 1] for fair MMR weighting
        max_rel = max(relevance) if relevance else 1.0
        if max_rel > 0:
            relevance = [r / max_rel for r in relevance]

        for _ in range(min(top_k, len(chunks))):
            best_idx = -1
            best_score = float("-inf")

            for idx in remaining:
                rel_score = relevance[idx]

                # Max similarity to already selected
                if selected:
                    max_sim = max(
                        _cosine_sim(embeddings[idx], embeddings[s]) for s in selected
                    )
                else:
                    max_sim = 0.0

                mmr_score = self._lambda * rel_score - (1 - self._lambda) * max_sim

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            if best_idx >= 0:
                selected.append(best_idx)
                remaining.remove(best_idx)

        return [
            replace(chunks[i], score=relevance[i]) for i in selected
        ]

    def _mmr_lexical(
        self,
        chunks: list[RetrievedChunkDTO],
        query: str,
        top_k: int,
    ) -> list[RetrievedChunkDTO]:
        """Fallback MMR using word overlap."""
        query_words = set(query.lower().split())
        selected: list[int] = []
        remaining = list(range(len(chunks)))

        for _ in range(min(top_k, len(chunks))):
            best_idx = -1
            best_score = float("-inf")

            for idx in remaining:
                chunk_words = set(chunks[idx].content.lower().split())
                rel = len(query_words & chunk_words) / max(len(query_words), 1)

                if selected:
                    max_sim = max(
                        _word_overlap(chunks[idx].content, chunks[s].content)
                        for s in selected
                    )
                else:
                    max_sim = 0.0

                mmr_score = self._lambda * rel - (1 - self._lambda) * max_sim
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            if best_idx >= 0:
                selected.append(best_idx)
                remaining.remove(best_idx)

        return [replace(chunks[i], score=chunks[i].score) for i in selected]


def _cosine_sim(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _word_overlap(a: str, b: str) -> float:
    wa = set(a.lower().split())
    wb = set(b.lower().split())
    union = wa | wb
    if not union:
        return 0.0
    return len(wa & wb) / len(union)



