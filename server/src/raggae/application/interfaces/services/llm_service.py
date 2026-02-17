from collections.abc import AsyncIterator
from typing import Protocol


class LLMService(Protocol):
    """Interface for text generation from a pre-built prompt."""

    async def generate_answer(self, prompt: str) -> str: ...

    def generate_answer_stream(self, prompt: str) -> AsyncIterator[str]: ...
