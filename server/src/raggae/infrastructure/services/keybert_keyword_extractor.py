import re
from collections import Counter
from typing import Protocol, cast


class _KeyBERTModel(Protocol):
    def extract_keywords(
        self,
        docs: str,
        *,
        keyphrase_ngram_range: tuple[int, int],
        stop_words: str,
        top_n: int,
    ) -> list[tuple[str, float]]: ...


class KeybertKeywordExtractor:
    """Keyword extractor using KeyBERT with TF-IDF fallback."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model: _KeyBERTModel | None = None

    async def extract_keywords(self, text: str, max_keywords: int = 10) -> list[str]:
        normalized = text.strip()
        if not normalized or max_keywords <= 0:
            return []

        try:
            keybert = self._get_model()
            if keybert is None:
                return self._extract_with_tfidf(normalized, max_keywords)
            raw = keybert.extract_keywords(
                normalized,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                top_n=max_keywords,
            )
            keywords = [kw for kw, _score in raw if isinstance(kw, str) and kw.strip()]
            if keywords:
                return keywords
        except Exception:
            return self._extract_with_tfidf(normalized, max_keywords)

        return self._extract_with_tfidf(normalized, max_keywords)

    def _get_model(self) -> _KeyBERTModel | None:
        if self._model is not None:
            return self._model
        try:
            from keybert import KeyBERT
        except ModuleNotFoundError:
            return None
        self._model = cast(_KeyBERTModel, KeyBERT(model=self._model_name))
        return self._model

    def _extract_with_tfidf(self, text: str, max_keywords: int) -> list[str]:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ModuleNotFoundError:
            return self._extract_with_frequency(text, max_keywords)

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=1000)
        matrix = vectorizer.fit_transform([text])
        scores = matrix.toarray()[0]
        features = vectorizer.get_feature_names_out()
        ranking = sorted(
            zip(features, scores, strict=False),
            key=lambda item: item[1],
            reverse=True,
        )
        return [term for term, score in ranking if score > 0][:max_keywords]

    def _extract_with_frequency(self, text: str, max_keywords: int) -> list[str]:
        words = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", text.lower())
        if not words:
            return []
        counts = Counter(words)
        return [word for word, _count in counts.most_common(max_keywords)]
