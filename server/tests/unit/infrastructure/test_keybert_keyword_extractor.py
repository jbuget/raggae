from raggae.infrastructure.services.keybert_keyword_extractor import (
    KeybertKeywordExtractor,
)


class TestKeybertKeywordExtractor:
    async def test_extract_keywords_returns_empty_for_blank_text(self) -> None:
        # Given
        extractor = KeybertKeywordExtractor()

        # When
        result = await extractor.extract_keywords("   ")

        # Then
        assert result == []

    async def test_extract_keywords_returns_keywords_for_regular_text(self) -> None:
        # Given
        extractor = KeybertKeywordExtractor()
        text = (
            "Workflow UB Bornes revue projet decision precommande borne "
            "expedition logistique mise en service abonnement."
        )

        # When
        result = await extractor.extract_keywords(text, max_keywords=5)

        # Then
        assert 1 <= len(result) <= 5

    async def test_extract_keywords_falls_back_when_keybert_fails(self) -> None:
        # Given
        extractor = KeybertKeywordExtractor()

        def _boom() -> object:
            raise RuntimeError("keybert unavailable")

        extractor._get_model = _boom  # type: ignore[method-assign]
        text = "alpha beta beta gamma gamma gamma"

        # When
        result = await extractor.extract_keywords(text, max_keywords=2)

        # Then
        assert result == ["gamma", "beta"]
