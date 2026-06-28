from raggae.application.dto.stats_dto import StatsTimeSeriesDTO
from raggae.application.interfaces.repositories.stats_repository import StatsRepository


class GetStatsTimeSeries:
    """Use Case: Return daily time series for the last `days` days."""

    def __init__(self, stats_repository: StatsRepository) -> None:
        self._stats_repository = stats_repository

    async def execute(self, days: int) -> StatsTimeSeriesDTO:
        return await self._stats_repository.get_timeseries(days)
