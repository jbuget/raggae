from typing import Annotated

from fastapi import APIRouter, Depends

from raggae.application.interfaces.repositories.agent_configuration_repository import (
    AgentConfigurationRepository,
)
from raggae.infrastructure.config.settings import settings
from raggae.presentation.api.dependencies import get_agent_configuration_repository
from raggae.presentation.api.v1.schemas.system_schemas import SystemDefaultsResponse

router = APIRouter(tags=["system"])


@router.get("/system/defaults", response_model=SystemDefaultsResponse)
async def get_system_defaults(
    repo: Annotated[AgentConfigurationRepository, Depends(get_agent_configuration_repository)],
) -> SystemDefaultsResponse:
    app_config = await repo.find_app_defaults()

    def _backend(stored: str | None, fallback: str) -> str:
        return (stored or fallback).lower()

    return SystemDefaultsResponse(
        llm_backend=_backend(app_config.llm_backend if app_config else None, settings.default_llm_provider),
        llm_model=app_config.llm_model or settings.default_llm_model
        if app_config
        else settings.default_llm_model,
        embedding_backend=_backend(
            app_config.embedding_backend if app_config else None, settings.default_embedding_provider
        ),
        embedding_model=app_config.embedding_model or settings.default_embedding_model
        if app_config
        else settings.default_embedding_model,
        chunking_strategy=app_config.chunking_strategy or settings.default_chunking_strategy
        if app_config
        else settings.default_chunking_strategy,
        parent_child_chunking=app_config.parent_child_chunking
        if app_config and app_config.parent_child_chunking is not None
        else settings.default_parent_child_chunking,
        retrieval_strategy=app_config.retrieval_strategy or settings.retrieval_default_strategy
        if app_config
        else settings.retrieval_default_strategy,
        retrieval_top_k=app_config.retrieval_top_k or settings.retrieval_default_chunk_limit
        if app_config
        else settings.retrieval_default_chunk_limit,
        retrieval_min_score=app_config.retrieval_min_score
        if app_config and app_config.retrieval_min_score is not None
        else settings.retrieval_min_score,
        reranker_backend=_backend(
            app_config.reranker_backend if app_config else None, settings.reranker_backend
        ),
        reranker_model=app_config.reranker_model or settings.reranker_model
        if app_config
        else settings.reranker_model,
        reranker_candidate_multiplier=app_config.reranker_candidate_multiplier
        or settings.reranker_candidate_multiplier
        if app_config
        else settings.reranker_candidate_multiplier,
        chat_history_window_size=app_config.chat_history_window_size or settings.chat_history_window_size
        if app_config
        else settings.chat_history_window_size,
        chat_history_max_chars=app_config.chat_history_max_chars or settings.chat_history_max_chars
        if app_config
        else settings.chat_history_max_chars,
    )
