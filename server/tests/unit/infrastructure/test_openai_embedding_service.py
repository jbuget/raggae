from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError
from raggae.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService


class TestOpenAIEmbeddingService:
    async def test_embed_texts_success(self) -> None:
        # Given
        service = OpenAIEmbeddingService(
            api_key="test-key",
            model="text-embedding-3-small",
            expected_dimension=2,
        )
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.embeddings.create.return_value = SimpleNamespace(
            data=[
                SimpleNamespace(embedding=[0.1, 0.2]),
                SimpleNamespace(embedding=[0.3, 0.4]),
            ]
        )

        # When
        result = await service.embed_texts(["hello", "world"])

        # Then
        assert result == [[0.1, 0.2], [0.3, 0.4]]

    async def test_embed_texts_provider_error_raises_domain_error(self) -> None:
        # Given
        service = OpenAIEmbeddingService(
            api_key="test-key",
            model="text-embedding-3-small",
            expected_dimension=2,
        )
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.embeddings.create.side_effect = RuntimeError("provider timeout")

        # When / Then
        with pytest.raises(EmbeddingGenerationError):
            await service.embed_texts(["hello"])

    async def test_embed_texts_wrong_dimension_raises_domain_error(self) -> None:
        # Given
        service = OpenAIEmbeddingService(
            api_key="test-key",
            model="text-embedding-3-small",
            expected_dimension=1536,
        )
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.embeddings.create.return_value = SimpleNamespace(
            data=[SimpleNamespace(embedding=[0.1, 0.2])]
        )

        # When / Then
        with pytest.raises(EmbeddingGenerationError, match="dimension"):
            await service.embed_texts(["hello"])
