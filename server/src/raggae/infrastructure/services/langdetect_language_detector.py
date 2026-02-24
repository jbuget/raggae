from typing import cast


class LangdetectLanguageDetector:
    """Language detector based on langdetect with conservative guards."""

    def __init__(self, minimum_chars: int = 20) -> None:
        self._minimum_chars = max(1, minimum_chars)

    async def detect_language(self, text: str) -> str | None:
        normalized = text.strip()
        if not normalized or len(normalized) < self._minimum_chars:
            return None

        try:
            from langdetect import detect
            from langdetect.lang_detect_exception import LangDetectException
        except ModuleNotFoundError:
            return None

        try:
            return cast(str, detect(normalized))
        except LangDetectException:
            return None
