import logging
from collections.abc import AsyncIterator
from time import perf_counter

from openai import AsyncOpenAI

from raggae.domain.exceptions.document_exceptions import LLMGenerationError

logger = logging.getLogger(__name__)


class OpenAILLMService:
    """LLM service implementation backed by OpenAI chat completions."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate_answer(self, prompt: str) -> str:
        started_at = perf_counter()
        logger.info(
            "llm_request_started",
            extra={"backend": "openai", "model": self._model},
        )
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.info(
                "llm_request_succeeded",
                extra={
                    "backend": "openai",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            return content or ""
        except Exception as exc:  # pragma: no cover - provider dependent
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_request_failed",
                extra={
                    "backend": "openai",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to generate answer: {exc}") from exc

    async def generate_answer_stream(self, prompt: str) -> AsyncIterator[str]:
        started_at = perf_counter()
        logger.info(
            "llm_stream_started",
            extra={"backend": "openai", "model": self._model},
        )
        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield delta
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.info(
                "llm_stream_succeeded",
                extra={
                    "backend": "openai",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
        except Exception as exc:  # pragma: no cover - provider dependent
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_stream_failed",
                extra={
                    "backend": "openai",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to stream answer: {exc}") from exc
