from typing import Protocol


class LanguageDetector(Protocol):
    """Interface to detect a document language from text."""

    async def detect_language(self, text: str) -> str | None: ...
