from unittest.mock import AsyncMock, Mock

import pytest

from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.infrastructure.services.gemini_llm_service import GeminiLLMService


class TestGeminiLLMService:
    async def test_generate_answer_success(self) -> None:
        # Given
        service = GeminiLLMService(api_key="test-key", model="gemini-1.5-flash")
        response = Mock()
        response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "answer"}],
                    }
                }
            ]
        }
        response.raise_for_status.return_value = None
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.post.return_value = response

        # When
        result = await service.generate_answer(query="What is RAG?", context_chunks=["chunk one"])

        # Then
        assert result == "answer"

    async def test_generate_answer_provider_error_raises_domain_error(self) -> None:
        # Given
        service = GeminiLLMService(api_key="test-key", model="gemini-1.5-flash")
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.post.side_effect = RuntimeError("provider timeout")

        # When / Then
        with pytest.raises(LLMGenerationError):
            await service.generate_answer(query="hello", context_chunks=[])
