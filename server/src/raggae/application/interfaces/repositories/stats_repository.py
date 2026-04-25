from abc import ABC, abstractmethod

from raggae.application.dto.stats_dto import StatsDTO


class StatsRepository(ABC):
    """Interface for computing platform-wide public statistics."""

    @abstractmethod
    async def get_stats(self) -> StatsDTO:
        """Return aggregated platform statistics."""
