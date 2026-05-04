import logging
import httpx

from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError

logger = logging.getLogger(__name__)


class GeminiEmbeddingService:
    """Embedding service implementation backed by Gemini REST API."""

    def __init__(self, api_key: str, model: str, expected_dimension: int | None = None) -> None:
        self._api_key = api_key
        self._model = model
        self._expected_dimension = expected_dimension
        self._client = httpx.AsyncClient(timeout=120.0)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings: list[list[float]] = []
        for text in texts:
            embedding = await self._embed_single(text)
            embeddings.append(embedding)
        return embeddings

    async def _embed_single(self, text: str) -> list[float]:
        logger.debug(
            "Gemini embedding request (model=%s, expected_dim=%s, text_len=%s)",
            self._model,
            self._expected_dimension,
            len(text),
        )
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
                    f"Invalid embedding dimension: expected {self._expected_dimension}, got {len(embedding)}"
                )
            return embedding
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Gemini embedding request failed (status=%s, body=%s)",
                exc.response.status_code,
                exc.response.text,
            )
            raise EmbeddingGenerationError(
                f"Failed to generate embeddings: status={exc.response.status_code}"
            ) from exc
        except EmbeddingGenerationError:
            raise
        except Exception as exc:  # pragma: no cover - provider dependent
            logger.exception("Gemini embedding request failed")
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {exc}") from exc
