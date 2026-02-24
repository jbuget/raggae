from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.infrastructure.services.openai_llm_service import OpenAILLMService


async def _async_iter(items: list[object]):  # type: ignore[type-arg]
    for item in items:
        yield item


class TestOpenAILLMService:
    async def test_generate_answer_success(self) -> None:
        # Given
        service = OpenAILLMService(api_key="test-key", model="gpt-4o-mini")
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="answer"))]
        )

        # When
        result = await service.generate_answer("What is RAG?")

        # Then
        assert result == "answer"

    async def test_generate_answer_provider_error_raises_domain_error(self) -> None:
        # Given
        service = OpenAILLMService(api_key="test-key", model="gpt-4o-mini")
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.chat.completions.create.side_effect = RuntimeError("provider timeout")

        # When / Then
        with pytest.raises(LLMGenerationError):
            await service.generate_answer("hello")

    async def test_generate_answer_stream_yields_tokens(self) -> None:
        # Given
        service = OpenAILLMService(api_key="test-key", model="gpt-4o-mini")
        service._client = AsyncMock()  # type: ignore[attr-defined]
        chunks = [
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Hello"))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=" world"))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=None))]),
        ]
        service._client.chat.completions.create.return_value = _async_iter(chunks)

        # When
        tokens: list[str] = []
        async for token in service.generate_answer_stream("What is RAG?"):
            tokens.append(token)

        # Then
        assert tokens == ["Hello", " world"]
