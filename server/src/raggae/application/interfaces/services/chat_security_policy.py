from typing import Protocol


class ChatSecurityPolicy(Protocol):
    """Application-level policy guard for chat security rules."""

    def is_disallowed_user_message(self, message: str) -> bool: ...

    def sanitize_model_answer(self, answer: str) -> str: ...
