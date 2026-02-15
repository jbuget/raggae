from typing import Protocol


class ConversationTitleGenerator(Protocol):
    """Interface for generating conversation titles from chat content."""

    async def generate_title(self, user_message: str, assistant_answer: str) -> str: ...
