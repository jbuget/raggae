from unittest.mock import AsyncMock, patch

import httpx
import pytest
from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError
from raggae.infrastructure.services.ollama_embedding_service import OllamaEmbeddingService


class TestOllamaEmbeddingService:
    @pytest.fixture
    def service(self) -> OllamaEmbeddingService:
        return OllamaEmbeddingService(
            base_url="http://localhost:11434",
            model="nomic-embed-text",
            expected_dimension=3,
        )

    async def test_embed_texts_returns_embeddings(self, service: OllamaEmbeddingService) -> None:
        # Given
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = lambda: None
        mock_response.json.side_effect = [
            {"embeddings": [[0.1, 0.2, 0.3]]},
            {"embeddings": [[0.4, 0.5, 0.6]]},
        ]

        with patch.object(service._client, "post", return_value=mock_response) as mock_post:
            # When
            result = await service.embed_texts(["hello", "world"])

            # Then
            assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            assert mock_post.call_count == 2

    async def test_embed_texts_empty_list_returns_empty(
        self, service: OllamaEmbeddingService
    ) -> None:
        # When
        result = await service.embed_texts([])

        # Then
        assert result == []

    async def test_embed_texts_http_error_raises_embedding_error(
        self, service: OllamaEmbeddingService
    ) -> None:
        # Given
        mock_request = httpx.Request("POST", "http://localhost:11434/api/embed")
        mock_resp = httpx.Response(500, request=mock_request)
        with patch.object(
            service._client,
            "post",
            side_effect=httpx.HTTPStatusError("500", request=mock_request, response=mock_resp),
        ):
            # When / Then
            with pytest.raises(EmbeddingGenerationError):
                await service.embed_texts(["hello"])

    async def test_embed_texts_sends_one_request_per_text(
        self, service: OllamaEmbeddingService
    ) -> None:
        # Given
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = lambda: None
        mock_response.json.side_effect = [
            {"embeddings": [[0.1, 0.2, 0.3]]},
            {"embeddings": [[0.3, 0.4, 0.5]]},
            {"embeddings": [[0.5, 0.6, 0.7]]},
        ]

        with patch.object(service._client, "post", return_value=mock_response) as mock_post:
            # When
            result = await service.embed_texts(["a", "b", "c"])

            # Then
            assert len(result) == 3
            assert mock_post.call_count == 3

    async def test_embed_texts_truncates_long_input(self) -> None:
        # Given
        max_chars = 500
        service = OllamaEmbeddingService(
            base_url="http://localhost:11434",
            model="nomic-embed-text",
            max_chars_per_text=max_chars,
        )
        long_text = "a" * 1000

        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = lambda: None
        mock_response.json.return_value = {"embeddings": [[0.1]]}

        with patch.object(service._client, "post", return_value=mock_response) as mock_post:
            # When
            await service.embed_texts([long_text])

            # Then
            sent_input = mock_post.call_args.kwargs["json"]["input"]
            assert len(sent_input) == max_chars

    async def test_embed_texts_strips_trailing_slash_from_base_url(self) -> None:
        # Given
        service = OllamaEmbeddingService(
            base_url="http://localhost:11434/",
            model="nomic-embed-text",
        )
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = lambda: None
        mock_response.json.return_value = {"embeddings": [[0.1]]}

        with patch.object(service._client, "post", return_value=mock_response) as mock_post:
            # When
            await service.embed_texts(["test"])

            # Then
            mock_post.assert_called_once_with(
                "http://localhost:11434/api/embed",
                json={"model": "nomic-embed-text", "input": "test"},
            )

    async def test_embed_texts_wrong_dimension_raises_embedding_error(self) -> None:
        # Given
        service = OllamaEmbeddingService(
            base_url="http://localhost:11434",
            model="nomic-embed-text",
            expected_dimension=1536,
        )
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = lambda: None
        mock_response.json.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}

        with patch.object(service._client, "post", return_value=mock_response):
            # When / Then
            with pytest.raises(EmbeddingGenerationError, match="dimension"):
                await service.embed_texts(["hello"])
