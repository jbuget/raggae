import hashlib
import re
from math import log, sqrt


_WORD_RE = re.compile(r"[a-zA-ZÀ-ÿ0-9]+")

# Common French + English stop words to ignore
_STOP_WORDS = frozenset({
    "le", "la", "les", "de", "du", "des", "un", "une", "et", "en", "est",
    "que", "qui", "dans", "pour", "par", "sur", "au", "aux", "ce", "se",
    "son", "sa", "ses", "il", "elle", "on", "nous", "vous", "ils", "ne",
    "pas", "plus", "avec", "ou", "mais", "sont", "être", "avoir", "fait",
    "the", "a", "an", "and", "or", "of", "to", "in", "is", "it", "for",
    "on", "at", "by", "this", "that", "with", "from", "as", "be", "not",
    "d", "l", "s", "n", "qu", "c", "j", "m",
})


class InMemoryEmbeddingService:
    """Deterministic embedding service for tests/dev without external calls.

    Uses a lightweight bag-of-words approach with stable hashing to produce
    embeddings where similar texts have higher cosine similarity — unlike
    raw SHA256 which produces uncorrelated vectors.
    """

    def __init__(self, dimension: int = 16) -> None:
        self._dimension = dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_single(text) for text in texts]

    def _embed_single(self, text: str) -> list[float]:
        words = _WORD_RE.findall(text.lower())
        # Filter stop words and very short tokens
        meaningful = [w for w in words if w not in _STOP_WORDS and len(w) > 1]

        if not meaningful:
            # Fallback: use SHA256 for empty/stop-word-only texts
            return self._sha256_fallback(text)

        # Build sparse bag-of-words vector projected to fixed dimension
        vector = [0.0] * self._dimension
        word_count: dict[str, int] = {}
        for word in meaningful:
            word_count[word] = word_count.get(word, 0) + 1

        total_words = len(meaningful)
        for word, count in word_count.items():
            # TF component: log-scaled term frequency
            tf = 1.0 + log(count) if count > 0 else 0.0
            # Hash word to a dimension bucket (deterministic)
            bucket = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % self._dimension
            # Alternate sign based on a second hash to reduce collisions
            sign = 1.0 if (int(hashlib.sha1(word.encode("utf-8")).hexdigest(), 16) % 2) == 0 else -1.0
            vector[bucket] += sign * tf

        # L2 normalize
        norm = sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    def _sha256_fallback(self, text: str) -> list[float]:
        """Fallback for texts with no meaningful words."""
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [byte / 255.0 for byte in digest]
        if self._dimension <= len(values):
            return values[: self._dimension]
        repeats = (self._dimension + len(values) - 1) // len(values)
        return (values * repeats)[: self._dimension]
