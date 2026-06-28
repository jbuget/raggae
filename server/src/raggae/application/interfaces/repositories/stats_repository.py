from abc import ABC, abstractmethod

from raggae.application.dto.stats_dto import StatsDTO, StatsTimeSeriesDTO


class StatsRepository(ABC):
    """Interface for computing platform-wide public statistics."""

    @abstractmethod
    async def get_stats(self) -> StatsDTO:
        """Return aggregated platform statistics."""

    @abstractmethod
    async def get_timeseries(self, days: int) -> StatsTimeSeriesDTO:
        """Return daily time series for the last `days` days (inclusive of today)."""
