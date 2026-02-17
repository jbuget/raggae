import httpx

from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError


class GeminiEmbeddingService:
    """Embedding service implementation backed by Gemini REST API."""

    def __init__(self, api_key: str, model: str, expected_dimension: int | None = None) -> None:
        self._api_key = api_key
        self._model = self._normalize_model_name(model)
        self._expected_dimension = expected_dimension
        self._client = httpx.AsyncClient(timeout=120.0)

    def _normalize_model_name(self, model: str) -> str:
        # Backward compatibility for deprecated aliases that now return 404.
        if model in {"embedding-001", "gemini-embedding-001"}:
            return "text-embedding-004"
        return model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings: list[list[float]] = []
        for text in texts:
            embedding = await self._embed_single(text)
            embeddings.append(embedding)
        return embeddings

    async def _embed_single(self, text: str) -> list[float]:
        payload: dict[str, object] = {
            "content": {
                "parts": [{"text": text}],
            }
        }
        if self._expected_dimension is not None:
            payload["outputDimensionality"] = self._expected_dimension

        try:
            response = await self._client.post(
                (
                    "https://generativelanguage.googleapis.com/v1beta/"
                    f"models/{self._model}:embedContent?key={self._api_key}"
                ),
                json=payload,
            )
            response.raise_for_status()
            embedding = list(response.json()["embedding"]["values"])
            if self._expected_dimension is not None and len(embedding) != self._expected_dimension:
                raise EmbeddingGenerationError(
                    "Invalid embedding dimension: "
                    f"expected {self._expected_dimension}, got {len(embedding)}"
                )
            return embedding
        except EmbeddingGenerationError:
            raise
        except Exception as exc:  # pragma: no cover - provider dependent
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {exc}") from exc
