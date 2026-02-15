from typing import Protocol


class EmbeddingService(Protocol):
    """Interface for generating vector embeddings."""

    async def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
