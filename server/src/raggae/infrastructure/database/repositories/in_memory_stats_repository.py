from datetime import UTC, datetime

from raggae.application.dto.stats_dto import (
    StatsDTO,
    StatsFonctionnementDTO,
    StatsImpactDTO,
    StatsUsageDTO,
)
from raggae.application.interfaces.repositories.stats_repository import StatsRepository


class InMemoryStatsRepository(StatsRepository):
    """In-memory stats repository returning zero values — for testing only."""

    async def get_stats(self) -> StatsDTO:
        return StatsDTO(
            generated_at=datetime.now(UTC),
            north_star_reliable_answers=0,
            fonctionnement=StatsFonctionnementDTO(
                indexing_success_rate_percent=0.0,
                projects_with_documents=0,
                total_document_size_mb=0.0,
                total_chunks=0,
            ),
            usage=StatsUsageDTO(
                users_total=0,
                users_active_30d=0,
                organizations_total=0,
                projects_total=0,
                projects_published=0,
                conversations_total=0,
                messages_total=0,
                documents_total=0,
            ),
            impact=StatsImpactDTO(
                reliable_answers_total=0,
                reliable_answers_rate_percent=0.0,
                average_reliability_percent=0.0,
                relevant_answers_rate_percent=0.0,
                multi_turn_conversations_rate_percent=0.0,
                average_sources_per_answer=0.0,
            ),
        )
