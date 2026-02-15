from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.infrastructure.services.openai_llm_service import OpenAILLMService


class TestOpenAILLMService:
    async def test_generate_answer_success(self) -> None:
        # Given
        service = OpenAILLMService(api_key="test-key", model="gpt-4o-mini")
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="answer"))]
        )

        # When
        result = await service.generate_answer(
            query="What is RAG?",
            context_chunks=["chunk one", "chunk two"],
        )

        # Then
        assert result == "answer"

    async def test_generate_answer_provider_error_raises_domain_error(self) -> None:
        # Given
        service = OpenAILLMService(api_key="test-key", model="gpt-4o-mini")
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.chat.completions.create.side_effect = RuntimeError("provider timeout")

        # When / Then
        with pytest.raises(LLMGenerationError):
            await service.generate_answer(query="hello", context_chunks=[])
