from raggae.application.dto.stats_dto import StatsDTO
from raggae.application.interfaces.repositories.stats_repository import StatsRepository


class GetPublicStats:
    """Use Case: Return aggregated public statistics for the platform."""

    def __init__(self, stats_repository: StatsRepository) -> None:
        self._stats_repository = stats_repository

    async def execute(self) -> StatsDTO:
        return await self._stats_repository.get_stats()
