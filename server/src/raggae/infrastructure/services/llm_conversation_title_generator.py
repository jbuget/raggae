from raggae.application.interfaces.services.conversation_title_generator import (
    ConversationTitleGenerator,
)
from raggae.application.interfaces.services.llm_service import LLMService


class LLMConversationTitleGenerator(ConversationTitleGenerator):
    """Generate a concise conversation title using the configured LLM backend."""

    def __init__(self, llm_service: LLMService) -> None:
        self._llm_service = llm_service

    async def generate_title(self, user_message: str, assistant_answer: str) -> str:
        prompt = (
            "Generate a short conversation title (max 8 words). "
            "Return only the title, no punctuation at the end."
        )
        context = [
            f"User message: {user_message}",
            f"Assistant answer: {assistant_answer}",
        ]
        return await self._llm_service.generate_answer(query=prompt, context_chunks=context)
