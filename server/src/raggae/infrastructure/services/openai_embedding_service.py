from openai import AsyncOpenAI

from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError


class OpenAIEmbeddingService:
    """Embedding service implementation backed by OpenAI."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as exc:  # pragma: no cover - provider dependent
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {exc}") from exc
