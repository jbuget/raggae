import httpx

from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.infrastructure.services.prompt_builder import build_rag_prompt


class OllamaLLMService:
    """LLM service implementation backed by Ollama HTTP API."""

    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
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
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            payload = response.json()
            return str(payload["response"])
        except Exception as exc:  # pragma: no cover - provider dependent
            raise LLMGenerationError(f"Failed to generate answer: {exc}") from exc
