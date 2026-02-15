from typing import Protocol


class TextSanitizerService(Protocol):
    """Interface for safe text sanitization before chunking."""

    async def sanitize_text(self, text: str) -> str: ...
