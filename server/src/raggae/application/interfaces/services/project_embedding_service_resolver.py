from typing import Protocol

from raggae.application.interfaces.services.embedding_service import EmbeddingService


class ProjectEmbeddingServiceResolver(Protocol):
    """Resolve the effective embedding service for a project."""

    def resolve(
        self,
        backend: str | None,
        model: str | None,
        encrypted_api_key: str | None,
    ) -> EmbeddingService: ...
