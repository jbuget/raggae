import logging
from time import perf_counter

import httpx

from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.infrastructure.services.prompt_builder import build_rag_prompt

logger = logging.getLogger(__name__)


class OllamaLLMService:
    """LLM service implementation backed by Ollama HTTP API."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float = 120.0,
        keep_alive: str = "10m",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._keep_alive = keep_alive
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def generate_answer(
        self,
        query: str,
        context_chunks: list[str],
        project_system_prompt: str | None = None,
    ) -> str:
        started_at = perf_counter()
        logger.info(
            "llm_request_started",
            extra={
                "backend": "ollama",
                "model": self._model,
                "query_length": len(query),
                "context_chunks_count": len(context_chunks),
            },
        )
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
                    "keep_alive": self._keep_alive,
                },
            )
            response.raise_for_status()
            payload = response.json()
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.info(
                "llm_request_succeeded",
                extra={
                    "backend": "ollama",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            return str(payload["response"])
        except Exception as exc:  # pragma: no cover - provider dependent
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_request_failed",
                extra={
                    "backend": "ollama",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to generate answer: {exc}") from exc
