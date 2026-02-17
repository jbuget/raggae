from typing import Protocol


class KeywordExtractor(Protocol):
    """Interface to extract keywords from text."""

    async def extract_keywords(self, text: str, max_keywords: int = 10) -> list[str]: ...
