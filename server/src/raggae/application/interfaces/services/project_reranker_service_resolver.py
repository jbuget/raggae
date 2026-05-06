from typing import Protocol

from raggae.application.interfaces.services.reranker_service import RerankerService


class ProjectRerankerServiceResolver(Protocol):
    """Resolve the effective reranker service from resolved config."""

    def resolve(
        self,
        reranking_enabled: bool | None,
        backend: str | None,
        model: str | None,
    ) -> RerankerService | None: ...
