from datetime import UTC, datetime, timedelta

from raggae.application.dto.stats_dto import (
    StatsDTO,
    StatsFonctionnementDTO,
    StatsImpactDTO,
    StatsTimeSeriesDTO,
    StatsUsageDTO,
    TimeSeriesPoint,
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

    async def get_timeseries(self, days: int) -> StatsTimeSeriesDTO:
        today = datetime.now(UTC).date()
        from_date = today - timedelta(days=days - 1)
        empty_series = [TimeSeriesPoint(date=from_date + timedelta(days=i), value=0) for i in range(days)]
        return StatsTimeSeriesDTO(
            generated_at=datetime.now(UTC),
            from_date=from_date,
            to_date=today,
            user_messages=list(empty_series),
            conversations=list(empty_series),
            daily_active_users=list(empty_series),
            reliable_answers=list(empty_series),
            documents_indexed=list(empty_series),
            projects_created=list(empty_series),
        )
