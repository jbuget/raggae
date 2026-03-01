from raggae.application.interfaces.services.reranker_service import RerankerService
from raggae.domain.entities.project import Project
from raggae.infrastructure.config.settings import Settings
from raggae.infrastructure.services.cross_encoder_reranker_service import (
    CrossEncoderRerankerService,
)
from raggae.infrastructure.services.in_memory_reranker_service import InMemoryRerankerService
from raggae.infrastructure.services.mmr_diversity_reranker_service import (
    MmrDiversityRerankerService,
)


class ProjectRerankerServiceResolver:
    """Resolve reranker service using project settings with global fallback."""

    def __init__(
        self,
        settings: Settings,
        default_reranker_service: RerankerService | None = None,
    ) -> None:
        self._settings = settings
        self._default_reranker_service = default_reranker_service

    def resolve(self, project: Project) -> RerankerService | None:
        if not project.reranking_enabled:
            return None

        backend = project.reranker_backend or self._settings.reranker_backend
        model = project.reranker_model or self._settings.reranker_model

        if backend == "none":
            return None

        if backend == "cross_encoder":
            return CrossEncoderRerankerService(model_name=model)
        if backend == "inmemory":
            return InMemoryRerankerService()
        if backend == "mmr":
            return MmrDiversityRerankerService(lambda_param=0.85)
        return self._default_reranker_service
