class InMemoryKeywordExtractor:
    """Deterministic keyword extractor for tests."""

    def __init__(self, keywords: list[str] | None = None) -> None:
        self._keywords = keywords or []

    async def extract_keywords(self, text: str, max_keywords: int = 10) -> list[str]:
        del text
        return self._keywords[: max(0, max_keywords)]
