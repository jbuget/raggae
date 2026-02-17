import logging
from collections.abc import AsyncIterator
from time import perf_counter

logger = logging.getLogger(__name__)


class InMemoryLLMService:
    """Deterministic LLM service for tests/dev without external calls."""

    async def generate_answer(self, prompt: str) -> str:
        started_at = perf_counter()
        logger.info(
            "llm_request_started",
            extra={"backend": "inmemory", "model": "inmemory"},
        )
        elapsed_ms = (perf_counter() - started_at) * 1000.0
        logger.info(
            "llm_request_succeeded",
            extra={
                "backend": "inmemory",
                "model": "inmemory",
                "elapsed_ms": round(elapsed_ms, 2),
            },
        )
        return f"Answer based on prompt ({len(prompt)} chars)"

    async def generate_answer_stream(self, prompt: str) -> AsyncIterator[str]:
        answer = await self.generate_answer(prompt)
        yield answer
