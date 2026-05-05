from fastapi import APIRouter

from raggae.infrastructure.config.settings import settings
from raggae.presentation.api.v1.schemas.system_schemas import SystemDefaultsResponse

router = APIRouter(tags=["system"])


@router.get("/system/defaults", response_model=SystemDefaultsResponse)
async def get_system_defaults() -> SystemDefaultsResponse:
    return SystemDefaultsResponse(
        llm_backend=settings.default_llm_provider,
        llm_model=settings.default_llm_model,
        embedding_backend=settings.default_embedding_provider,
        embedding_model=settings.default_embedding_model,
        retrieval_strategy=settings.retrieval_default_strategy,
        retrieval_top_k=settings.retrieval_default_chunk_limit,
        retrieval_min_score=settings.retrieval_min_score,
        reranker_backend=settings.reranker_backend,
        reranker_model=settings.reranker_model,
        reranker_candidate_multiplier=settings.reranker_candidate_multiplier,
        chat_history_window_size=settings.chat_history_window_size,
        chat_history_max_chars=settings.chat_history_max_chars,
    )
