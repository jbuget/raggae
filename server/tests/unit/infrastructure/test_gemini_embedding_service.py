from unittest.mock import AsyncMock, Mock

import pytest
from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError
from raggae.infrastructure.services.gemini_embedding_service import GeminiEmbeddingService


class TestGeminiEmbeddingService:
    async def test_embed_texts_success(self) -> None:
        # Given
        service = GeminiEmbeddingService(
            api_key="test-key",
            model="gemini-embedding-001",
            expected_dimension=3,
        )
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.side_effect = [
            {"embedding": {"values": [0.1, 0.2, 0.3]}},
            {"embedding": {"values": [0.4, 0.5, 0.6]}},
        ]
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.post.return_value = response

        # When
        result = await service.embed_texts(["hello", "world"])

        # Then
        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        assert service._client.post.call_count == 2

    async def test_embed_texts_empty_list_returns_empty(self) -> None:
        # Given
        service = GeminiEmbeddingService(
            api_key="test-key",
            model="gemini-embedding-001",
            expected_dimension=1536,
        )

        # When
        result = await service.embed_texts([])

        # Then
        assert result == []

    async def test_embed_texts_provider_error_raises_domain_error(self) -> None:
        # Given
        service = GeminiEmbeddingService(
            api_key="test-key",
            model="gemini-embedding-001",
            expected_dimension=1536,
        )
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.post.side_effect = RuntimeError("provider timeout")

        # When / Then
        with pytest.raises(EmbeddingGenerationError):
            await service.embed_texts(["hello"])

    async def test_embed_texts_wrong_dimension_raises_domain_error(self) -> None:
        # Given
        service = GeminiEmbeddingService(
            api_key="test-key",
            model="gemini-embedding-001",
            expected_dimension=1536,
        )
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"embedding": {"values": [0.1, 0.2]}}
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.post.return_value = response

        # When / Then
        with pytest.raises(EmbeddingGenerationError, match="dimension"):
            await service.embed_texts(["hello"])
