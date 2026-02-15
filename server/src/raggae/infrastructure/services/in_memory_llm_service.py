import logging
from collections.abc import AsyncIterator
from time import perf_counter

logger = logging.getLogger(__name__)


class InMemoryLLMService:
    """Deterministic LLM service for tests/dev without external calls."""

    async def generate_answer(
        self,
        query: str,
        context_chunks: list[str],
        project_system_prompt: str | None = None,
        conversation_history: list[str] | None = None,
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

    async def generate_answer_stream(
        self,
        query: str,
        context_chunks: list[str],
        project_system_prompt: str | None = None,
        conversation_history: list[str] | None = None,
    ) -> AsyncIterator[str]:
        answer = await self.generate_answer(
            query=query,
            context_chunks=context_chunks,
            project_system_prompt=project_system_prompt,
            conversation_history=conversation_history,
        )
        yield answer
