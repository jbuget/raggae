import hashlib


class InMemoryEmbeddingService:
    """Deterministic embedding service for tests/dev without external calls."""

    def __init__(self, dimension: int = 16) -> None:
        self._dimension = dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_single(text) for text in texts]

    def _embed_single(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [byte / 255.0 for byte in digest]
        if self._dimension <= len(values):
            return values[: self._dimension]
        repeats = (self._dimension + len(values) - 1) // len(values)
        return (values * repeats)[: self._dimension]
