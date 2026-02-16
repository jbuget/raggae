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
        results: list[list[float]] = []
        for text in texts:
            embedding = await self._embed_single(text)
            results.append(embedding)
        return results

    async def _embed_single(self, text: str) -> list[float]:
        try:
            response = await self._client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": text},
            )
            response.raise_for_status()
            payload = response.json()
            return list(payload["embeddings"][0])
        except httpx.HTTPStatusError as exc:
            body = exc.response.text if exc.response is not None else ""
            raise EmbeddingGenerationError(
                f"Ollama embed returned {exc.response.status_code}: {body}"
            ) from exc
        except Exception as exc:
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {exc}") from exc
