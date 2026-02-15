from typing import Protocol


class DocumentTextExtractor(Protocol):
    """Interface to extract text from binary document content."""

    async def extract_text(self, file_name: str, content: bytes, content_type: str) -> str: ...
