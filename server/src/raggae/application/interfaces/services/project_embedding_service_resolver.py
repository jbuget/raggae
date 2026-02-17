from typing import Protocol

from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.domain.entities.project import Project


class ProjectEmbeddingServiceResolver(Protocol):
    """Resolve the effective embedding service for a project."""

    def resolve(self, project: Project) -> EmbeddingService: ...
