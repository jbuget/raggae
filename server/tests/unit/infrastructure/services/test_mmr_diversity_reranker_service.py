import asyncio
from uuid import uuid4

import pytest

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.infrastructure.services.mmr_diversity_reranker_service import MmrDiversityRerankerService


def _chunk(content: str, score: float) -> RetrievedChunkDTO:
    return RetrievedChunkDTO(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content=content,
        score=score,
    )


class TestMmrDiversityRerankerServiceLexical:
    """Tests for the lexical MMR path (no embeddings provided)."""

    @pytest.fixture
    def reranker(self) -> MmrDiversityRerankerService:
        return MmrDiversityRerankerService(lambda_param=0.85)

    @pytest.mark.asyncio
    async def test_rerank_empty_returns_empty(self, reranker: MmrDiversityRerankerService) -> None:
        result = await reranker.rerank("CRAFT", [], top_k=5)
        assert result == []

    @pytest.mark.asyncio
    async def test_rerank_top_k_zero_returns_empty(self, reranker: MmrDiversityRerankerService) -> None:
        chunks = [_chunk("CRAFT formalisme", 0.9)]
        result = await reranker.rerank("CRAFT", chunks, top_k=0)
        assert result == []

    @pytest.mark.asyncio
    async def test_rerank_fewer_chunks_than_top_k_returns_all(self, reranker: MmrDiversityRerankerService) -> None:
        chunks = [_chunk("CRAFT formalisme", 0.9), _chunk("autre sujet", 0.5)]
        result = await reranker.rerank("CRAFT", chunks, top_k=10)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_rerank_uses_hybrid_score_as_relevance(self, reranker: MmrDiversityRerankerService) -> None:
        """When hybrid scores differ greatly, high-score chunks should be selected first
        even if word-overlap with the query is the same."""
        query = "qu'est-ce que CRAFT ?"
        # CRAFT chunks: high hybrid score, contain "CRAFT"
        craft_chunk_1 = _chunk("06.\nFormalisme CRAFT / CRAFT+\nUn cadre en 5 dimensions", 0.94)
        craft_chunk_2 = _chunk("CRAFT n'est pas un formulaire à remplir à chaque fois.", 0.68)
        # Generic IA chunks: low hybrid score, contain "que" from the query
        generic_chunk = _chunk("L'IA génère du texte que vous utilisez dans votre travail.", 0.30)

        chunks = [craft_chunk_1, generic_chunk, craft_chunk_2]
        result = await reranker.rerank(query, chunks, top_k=2)

        # Both selected chunks should be CRAFT-related
        selected_contents = [c.content for c in result]
        assert craft_chunk_1.content in selected_contents
        assert generic_chunk.content not in selected_contents

    @pytest.mark.asyncio
    async def test_rerank_high_score_chunk_selected_first(self, reranker: MmrDiversityRerankerService) -> None:
        """The highest-scored chunk should be selected first."""
        query = "CRAFT"
        high = _chunk("CRAFT est un formalisme de prompting.", 0.95)
        low = _chunk("CRAFT peut être utilisé dans divers cas.", 0.40)
        result = await reranker.rerank(query, [low, high], top_k=1)
        assert result[0].content == high.content

    @pytest.mark.asyncio
    async def test_rerank_zero_score_fallback_to_word_overlap(self, reranker: MmrDiversityRerankerService) -> None:
        """When all chunks have score=0, word overlap is used as fallback."""
        query = "CRAFT formalisme"
        matching = _chunk("CRAFT formalisme de prompt", 0.0)
        non_matching = _chunk("L'histoire de l'IA depuis 1950", 0.0)
        result = await reranker.rerank(query, [non_matching, matching], top_k=1)
        assert result[0].content == matching.content
