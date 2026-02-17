class InMemoryLanguageDetector:
    """Deterministic language detector for tests."""

    def __init__(self, language: str | None = "en") -> None:
        self._language = language

    async def detect_language(self, text: str) -> str | None:
        if not text.strip():
            return None
        return self._language
