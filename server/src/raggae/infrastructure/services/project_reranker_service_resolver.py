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
    """Resolve reranker service from resolved config with global fallback.

    Instances are cached by ``(backend, model)`` so that heavy models
    (e.g. CrossEncoder BERT weights) are loaded only once for the whole
    process lifetime.
    """

    def __init__(
        self,
        settings: Settings,
        default_reranker_service: RerankerService | None = None,
    ) -> None:
        self._settings = settings
        self._default_reranker_service = default_reranker_service
        self._cache: dict[tuple[str, str], RerankerService] = {}

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

        cache_key = (effective_backend, effective_model or "")
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        instance: RerankerService | None
        if effective_backend == "cross_encoder":
            instance = CrossEncoderRerankerService(model_name=effective_model)
        elif effective_backend == "inmemory":
            instance = InMemoryRerankerService()
        elif effective_backend == "mmr":
            instance = MmrDiversityRerankerService(lambda_param=0.85)
        else:
            return self._default_reranker_service

        self._cache[cache_key] = instance
        return instance
