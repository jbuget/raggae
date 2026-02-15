import logging
from time import perf_counter

logger = logging.getLogger(__name__)


class InMemoryLLMService:
    """Deterministic LLM service for tests/dev without external calls."""

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
                "backend": "inmemory",
                "model": "inmemory",
                "query_length": len(query),
                "context_chunks_count": len(context_chunks),
            },
        )
        if not context_chunks:
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.info(
                "llm_request_succeeded",
                extra={
                    "backend": "inmemory",
                    "model": "inmemory",
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            return f"No relevant context found for: {query}"
        elapsed_ms = (perf_counter() - started_at) * 1000.0
        logger.info(
            "llm_request_succeeded",
            extra={
                "backend": "inmemory",
                "model": "inmemory",
                "elapsed_ms": round(elapsed_ms, 2),
            },
        )
        return f"Answer based on {len(context_chunks)} chunks: {query}"
