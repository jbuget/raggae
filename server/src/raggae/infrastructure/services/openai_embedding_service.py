from openai import AsyncOpenAI

from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError


class OpenAIEmbeddingService:
    """Embedding service implementation backed by OpenAI."""

    def __init__(self, api_key: str, model: str, expected_dimension: int | None = None) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._expected_dimension = expected_dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=texts,
            )
            embeddings = [item.embedding for item in response.data]
            self._validate_dimensions(embeddings)
            return embeddings
        except EmbeddingGenerationError:
            raise
        except Exception as exc:  # pragma: no cover - provider dependent
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {exc}") from exc

    def _validate_dimensions(self, embeddings: list[list[float]]) -> None:
        if self._expected_dimension is None:
            return
        for embedding in embeddings:
            if len(embedding) != self._expected_dimension:
                raise EmbeddingGenerationError(
                    "Invalid embedding dimension: "
                    f"expected {self._expected_dimension}, got {len(embedding)}"
                )
