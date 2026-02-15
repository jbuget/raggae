import httpx

from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.infrastructure.services.prompt_builder import build_rag_prompt


class GeminiLLMService:
    """LLM service implementation backed by Gemini REST API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(timeout=30.0)

    async def generate_answer(
        self,
        query: str,
        context_chunks: list[str],
        project_system_prompt: str | None = None,
    ) -> str:
        prompt = build_rag_prompt(
            query=query,
            context_chunks=context_chunks,
            project_system_prompt=project_system_prompt,
        )
        try:
            response = await self._client.post(
                (
                    "https://generativelanguage.googleapis.com/v1beta/"
                    f"models/{self._model}:generateContent?key={self._api_key}"
                ),
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            response.raise_for_status()
            payload = response.json()
            return str(payload["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as exc:  # pragma: no cover - provider dependent
            raise LLMGenerationError(f"Failed to generate answer: {exc}") from exc
