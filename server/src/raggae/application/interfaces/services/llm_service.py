from typing import Protocol


class LLMService(Protocol):
    """Interface for text generation from retrieved context."""

    async def generate_answer(
        self,
        query: str,
        context_chunks: list[str],
        project_system_prompt: str | None = None,
        conversation_history: list[str] | None = None,
    ) -> str: ...
