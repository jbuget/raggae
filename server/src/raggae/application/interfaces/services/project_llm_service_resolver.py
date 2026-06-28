from typing import Protocol

from raggae.application.interfaces.services.llm_service import LLMService


class ProjectLLMServiceResolver(Protocol):
    """Resolve the effective LLM service from resolved config."""

    def resolve(
        self,
        backend: str | None,
        model: str | None,
        encrypted_api_key: str | None,
    ) -> LLMService: ...
