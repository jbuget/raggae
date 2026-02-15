from typing import Protocol


class TextChunkerService(Protocol):
    """Interface for splitting text into chunks."""

    async def chunk_text(self, text: str) -> list[str]: ...
