from raggae.application.interfaces.services.reranker_service import RerankerService
from raggae.infrastructure.config.settings import Settings
from raggae.infrastructure.services.cross_encoder_reranker_service import (
    CrossEncoderRerankerService,
)
from raggae.infrastructure.services.in_memory_reranker_service import InMemoryRerankerService
from raggae.infrastructure.services.mmr_diversity_reranker_service import (
    MmrDiversityRerankerService,
)


class ProjectRerankerServiceResolver:
    """Resolve reranker service from resolved config with global fallback."""

    def __init__(
        self,
        settings: Settings,
        default_reranker_service: RerankerService | None = None,
    ) -> None:
        self._settings = settings
        self._default_reranker_service = default_reranker_service

    def resolve(
        self,
        reranking_enabled: bool | None,
        backend: str | None,
        model: str | None,
    ) -> RerankerService | None:
        if reranking_enabled is False:
            return None

        effective_backend = backend or self._settings.reranker_backend
        effective_model = model or self._settings.reranker_model

        if effective_backend == "none":
            return None
        if effective_backend == "cross_encoder":
            return CrossEncoderRerankerService(model_name=effective_model)
        if effective_backend == "inmemory":
            return InMemoryRerankerService()
        if effective_backend == "mmr":
            return MmrDiversityRerankerService(lambda_param=0.85)
        return self._default_reranker_service
