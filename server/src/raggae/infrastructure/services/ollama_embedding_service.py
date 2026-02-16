import httpx

from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError


class OllamaEmbeddingService:
    """Embedding service implementation backed by Ollama HTTP API."""

    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = await self._client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": texts},
            )
            response.raise_for_status()
            payload = response.json()
            return [list(e) for e in payload["embeddings"]]
        except Exception as exc:
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {exc}") from exc
