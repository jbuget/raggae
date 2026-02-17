import sys
import types

import pytest

from raggae.infrastructure.services.langdetect_language_detector import (
    LangdetectLanguageDetector,
)


class TestLangdetectLanguageDetector:
    async def test_detect_language_returns_none_for_empty_text(self) -> None:
        # Given
        detector = LangdetectLanguageDetector()

        # When
        result = await detector.detect_language("  ")

        # Then
        assert result is None

    async def test_detect_language_returns_none_for_too_short_text(self) -> None:
        # Given
        detector = LangdetectLanguageDetector(minimum_chars=50)

        # When
        result = await detector.detect_language("Bonjour")

        # Then
        assert result is None

    async def test_detect_language_detects_french(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Given
        detector = LangdetectLanguageDetector(minimum_chars=20)
        text = "Ceci est un document en francais avec assez de contenu pour detection."
        fake_exc_mod = types.SimpleNamespace(LangDetectException=Exception)
        fake_mod = types.SimpleNamespace(detect=lambda _: "fr")
        monkeypatch.setitem(sys.modules, "langdetect", fake_mod)
        monkeypatch.setitem(sys.modules, "langdetect.lang_detect_exception", fake_exc_mod)

        # When
        result = await detector.detect_language(text)

        # Then
        assert result == "fr"

    async def test_detect_language_detects_english(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given
        detector = LangdetectLanguageDetector(minimum_chars=20)
        text = "This is an English document with enough words to detect the language."
        fake_exc_mod = types.SimpleNamespace(LangDetectException=Exception)
        fake_mod = types.SimpleNamespace(detect=lambda _: "en")
        monkeypatch.setitem(sys.modules, "langdetect", fake_mod)
        monkeypatch.setitem(sys.modules, "langdetect.lang_detect_exception", fake_exc_mod)

        # When
        result = await detector.detect_language(text)

        # Then
        assert result == "en"
