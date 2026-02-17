from typing import Protocol

from raggae.application.interfaces.services.llm_service import LLMService
from raggae.domain.entities.project import Project


class ProjectLLMServiceResolver(Protocol):
    """Resolve the effective llm service for a project."""

    def resolve(self, project: Project) -> LLMService: ...
