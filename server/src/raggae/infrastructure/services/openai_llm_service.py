from openai import AsyncOpenAI

from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.infrastructure.services.prompt_builder import build_rag_prompt


class OpenAILLMService:
    """LLM service implementation backed by OpenAI chat completions."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate_answer(self, query: str, context_chunks: list[str]) -> str:
        prompt = build_rag_prompt(query=query, context_chunks=context_chunks)
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content
            return content or ""
        except Exception as exc:  # pragma: no cover - provider dependent
            raise LLMGenerationError(f"Failed to generate answer: {exc}") from exc
