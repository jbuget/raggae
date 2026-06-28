from datetime import UTC, date, datetime
from unittest.mock import AsyncMock

import pytest

from raggae.application.dto.stats_dto import StatsTimeSeriesDTO, TimeSeriesPoint
from raggae.application.use_cases.stats.get_stats_timeseries import GetStatsTimeSeries


class TestGetStatsTimeSeries:
    @pytest.fixture
    def mock_stats_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_stats_repository: AsyncMock) -> GetStatsTimeSeries:
        return GetStatsTimeSeries(stats_repository=mock_stats_repository)

    async def test_execute_delegates_to_repository_with_days(
        self,
        use_case: GetStatsTimeSeries,
        mock_stats_repository: AsyncMock,
    ) -> None:
        # Given
        expected = StatsTimeSeriesDTO(
            generated_at=datetime.now(UTC),
            from_date=date(2026, 3, 31),
            to_date=date(2026, 6, 28),
            user_messages=[TimeSeriesPoint(date=date(2026, 6, 28), value=3)],
            conversations=[],
            daily_active_users=[],
            reliable_answers=[],
            documents_indexed=[],
            projects_created=[],
        )
        mock_stats_repository.get_timeseries.return_value = expected

        # When
        result = await use_case.execute(days=90)

        # Then
        assert result is expected
        mock_stats_repository.get_timeseries.assert_awaited_once_with(90)

    async def test_execute_propagates_days_parameter(
        self,
        use_case: GetStatsTimeSeries,
        mock_stats_repository: AsyncMock,
    ) -> None:
        # Given
        mock_stats_repository.get_timeseries.return_value = StatsTimeSeriesDTO(
            generated_at=datetime.now(UTC),
            from_date=date(2026, 6, 22),
            to_date=date(2026, 6, 28),
            user_messages=[],
            conversations=[],
            daily_active_users=[],
            reliable_answers=[],
            documents_indexed=[],
            projects_created=[],
        )

        # When
        await use_case.execute(days=7)

        # Then
        mock_stats_repository.get_timeseries.assert_awaited_once_with(7)
