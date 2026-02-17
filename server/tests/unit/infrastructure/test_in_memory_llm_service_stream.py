from raggae.infrastructure.services.in_memory_llm_service import InMemoryLLMService


class TestInMemoryLLMServiceStream:
    async def test_generate_answer_stream_yields_full_answer(self) -> None:
        # Given
        service = InMemoryLLMService()

        # When
        tokens: list[str] = []
        async for token in service.generate_answer_stream("What is RAG?"):
            tokens.append(token)

        # Then
        assert len(tokens) == 1
        assert "chars)" in tokens[0]

    async def test_generate_answer_returns_deterministic_response(self) -> None:
        # Given
        service = InMemoryLLMService()

        # When
        result = await service.generate_answer("test prompt")

        # Then
        assert "prompt" in result
