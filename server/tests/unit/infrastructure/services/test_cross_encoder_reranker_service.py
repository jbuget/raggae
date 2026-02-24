from unittest.mock import MagicMock
from uuid import uuid4

import numpy as np
import pytest
from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.infrastructure.services.cross_encoder_reranker_service import (
    CrossEncoderRerankerService,
)


def _make_chunk(content: str, score: float = 0.5) -> RetrievedChunkDTO:
    return RetrievedChunkDTO(
        chunk_id=uuid4(),
        document_id=uuid4(),
        content=content,
        score=score,
    )


class TestCrossEncoderRerankerService:
    async def test_rerank_returns_top_k_sorted_by_score(self) -> None:
        # Given
        service = CrossEncoderRerankerService(model_name="test-model")
        chunks = [
            _make_chunk("low relevance"),
            _make_chunk("high relevance"),
            _make_chunk("medium relevance"),
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0.1, 0.9, 0.5])
        service._model = mock_model

        # When
        result = await service.rerank("test query", chunks, top_k=2)

        # Then
        assert len(result) == 2
        assert result[0].content == "high relevance"
        assert result[0].score == pytest.approx(0.9)
        assert result[1].content == "medium relevance"
        assert result[1].score == pytest.approx(0.5)
        mock_model.predict.assert_called_once()

    async def test_rerank_empty_chunks_returns_empty(self) -> None:
        # Given
        service = CrossEncoderRerankerService()

        # When
        result = await service.rerank("query", [], top_k=5)

        # Then
        assert result == []

    async def test_model_loaded_lazily(self) -> None:
        # Given
        service = CrossEncoderRerankerService(model_name="test-model")

        # Then — model not loaded at construction time
        assert service._model is None

        # When — injecting a model simulates lazy load having occurred
        mock_model = MagicMock()
        service._model = mock_model

        # Then — _get_model returns the cached model without re-importing
        assert service._get_model() is mock_model

    async def test_rerank_preserves_chunk_metadata(self) -> None:
        # Given
        service = CrossEncoderRerankerService()
        doc_id = uuid4()
        chunk_id = uuid4()
        chunk = RetrievedChunkDTO(
            chunk_id=chunk_id,
            document_id=doc_id,
            content="important content",
            score=0.0,
            document_file_name="test.pdf",
        )
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0.85])
        service._model = mock_model

        # When
        result = await service.rerank("query", [chunk], top_k=1)

        # Then
        assert result[0].chunk_id == chunk_id
        assert result[0].document_id == doc_id
        assert result[0].document_file_name == "test.pdf"
        assert result[0].score == pytest.approx(0.85)
