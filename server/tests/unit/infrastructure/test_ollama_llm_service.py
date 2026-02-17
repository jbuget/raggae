from unittest.mock import AsyncMock, Mock

import pytest

from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.infrastructure.services.ollama_llm_service import OllamaLLMService


class TestOllamaLLMService:
    async def test_generate_answer_success(self) -> None:
        # Given
        service = OllamaLLMService(base_url="http://localhost:11434", model="llama3.1")
        response = Mock()
        response.json.return_value = {"response": "answer"}
        response.raise_for_status.return_value = None
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.post.return_value = response

        # When
        result = await service.generate_answer("What is RAG?")

        # Then
        assert result == "answer"

    async def test_generate_answer_provider_error_raises_domain_error(self) -> None:
        # Given
        service = OllamaLLMService(base_url="http://localhost:11434", model="llama3.1")
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.post.side_effect = RuntimeError("provider timeout")

        # When / Then
        with pytest.raises(LLMGenerationError):
            await service.generate_answer("hello")
