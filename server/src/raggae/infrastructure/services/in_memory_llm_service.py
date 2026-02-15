class InMemoryLLMService:
    """Deterministic LLM service for tests/dev without external calls."""

    async def generate_answer(
        self,
        query: str,
        context_chunks: list[str],
        project_system_prompt: str | None = None,
    ) -> str:
        if not context_chunks:
            return f"No relevant context found for: {query}"
        return f"Answer based on {len(context_chunks)} chunks: {query}"
