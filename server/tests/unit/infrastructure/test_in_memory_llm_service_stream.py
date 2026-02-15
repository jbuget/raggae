from raggae.infrastructure.services.in_memory_llm_service import InMemoryLLMService


class TestInMemoryLLMServiceStream:
    async def test_generate_answer_stream_yields_full_answer(self) -> None:
        # Given
        service = InMemoryLLMService()

        # When
        tokens: list[str] = []
        async for token in service.generate_answer_stream(
            query="What is RAG?",
            context_chunks=["chunk one", "chunk two"],
        ):
            tokens.append(token)

        # Then
        assert len(tokens) == 1
        assert tokens[0] == "Answer based on 2 chunks: What is RAG?"

    async def test_generate_answer_stream_no_chunks(self) -> None:
        # Given
        service = InMemoryLLMService()

        # When
        tokens: list[str] = []
        async for token in service.generate_answer_stream(
            query="hello",
            context_chunks=[],
        ):
            tokens.append(token)

        # Then
        assert tokens == ["No relevant context found for: hello"]
