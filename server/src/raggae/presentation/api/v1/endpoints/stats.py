from typing import Annotated

from fastapi import APIRouter, Depends

from raggae.application.use_cases.stats.get_public_stats import GetPublicStats
from raggae.presentation.api.dependencies import get_current_user_id, get_get_public_stats_use_case
from raggae.presentation.api.v1.schemas.stats_schemas import (
    StatsFonctionnementResponse,
    StatsImpactResponse,
    StatsResponse,
    StatsUsageResponse,
)

router = APIRouter(prefix="/stats", tags=["stats"], dependencies=[Depends(get_current_user_id)])


@router.get("", response_model=StatsResponse)
async def get_stats(
    use_case: Annotated[GetPublicStats, Depends(get_get_public_stats_use_case)],
) -> StatsResponse:
    """Returns aggregated platform statistics. Authentication required."""
    dto = await use_case.execute()
    return StatsResponse(
        generated_at=dto.generated_at,
        north_star_reliable_answers=dto.north_star_reliable_answers,
        fonctionnement=StatsFonctionnementResponse(
            indexing_success_rate_percent=dto.fonctionnement.indexing_success_rate_percent,
            projects_with_documents=dto.fonctionnement.projects_with_documents,
            total_document_size_mb=dto.fonctionnement.total_document_size_mb,
            total_chunks=dto.fonctionnement.total_chunks,
        ),
        usage=StatsUsageResponse(
            users_total=dto.usage.users_total,
            users_active_30d=dto.usage.users_active_30d,
            organizations_total=dto.usage.organizations_total,
            projects_total=dto.usage.projects_total,
            projects_published=dto.usage.projects_published,
            conversations_total=dto.usage.conversations_total,
            messages_total=dto.usage.messages_total,
            documents_total=dto.usage.documents_total,
        ),
        impact=StatsImpactResponse(
            reliable_answers_total=dto.impact.reliable_answers_total,
            reliable_answers_rate_percent=dto.impact.reliable_answers_rate_percent,
            average_reliability_percent=dto.impact.average_reliability_percent,
            relevant_answers_rate_percent=dto.impact.relevant_answers_rate_percent,
            multi_turn_conversations_rate_percent=dto.impact.multi_turn_conversations_rate_percent,
            average_sources_per_answer=dto.impact.average_sources_per_answer,
        ),
    )
