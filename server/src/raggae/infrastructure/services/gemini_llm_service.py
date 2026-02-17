import json
import logging
from collections.abc import AsyncIterator
from time import perf_counter

import httpx

from raggae.domain.exceptions.document_exceptions import LLMGenerationError

logger = logging.getLogger(__name__)


class GeminiLLMService:
    """LLM service implementation backed by Gemini REST API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    async def generate_answer(self, prompt: str) -> str:
        started_at = perf_counter()
        logger.info(
            "llm_request_started",
            extra={"backend": "gemini", "model": self._model},
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
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.info(
                "llm_request_succeeded",
                extra={
                    "backend": "gemini",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            return str(payload["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as exc:  # pragma: no cover - provider dependent
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_request_failed",
                extra={
                    "backend": "gemini",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to generate answer: {exc}") from exc

    async def generate_answer_stream(self, prompt: str) -> AsyncIterator[str]:
        started_at = perf_counter()
        logger.info(
            "llm_stream_started",
            extra={"backend": "gemini", "model": self._model},
        )
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/"
                f"models/{self._model}:streamGenerateContent?alt=sse&key={self._api_key}"
            )
            async with self._client.stream(
                "POST",
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = json.loads(line[len("data: ") :])
                    candidates = payload.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            text = part.get("text", "")
                            if text:
                                yield text
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.info(
                "llm_stream_succeeded",
                extra={
                    "backend": "gemini",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
        except Exception as exc:  # pragma: no cover - provider dependent
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_stream_failed",
                extra={
                    "backend": "gemini",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to stream answer: {exc}") from exc
