from typing import Protocol

from raggae.application.interfaces.services.reranker_service import RerankerService
from raggae.domain.entities.project import Project


class ProjectRerankerServiceResolver(Protocol):
    """Resolve the effective reranker service for a project."""

    def resolve(self, project: Project) -> RerankerService | None: ...
