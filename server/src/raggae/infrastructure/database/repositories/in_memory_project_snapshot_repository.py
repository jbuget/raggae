from uuid import UUID

from raggae.domain.entities.project_snapshot import ProjectSnapshot


class InMemoryProjectSnapshotRepository:
    """In-memory project snapshot repository for testing."""

    def __init__(self) -> None:
        self._snapshots: list[ProjectSnapshot] = []

    async def save(self, snapshot: ProjectSnapshot) -> None:
        self._snapshots.append(snapshot)

    async def find_by_project_and_version(
        self,
        project_id: UUID,
        version_number: int,
    ) -> ProjectSnapshot | None:
        return next(
            (s for s in self._snapshots if s.project_id == project_id and s.version_number == version_number),
            None,
        )

    async def find_by_project_id(
        self,
        project_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ProjectSnapshot]:
        matching = [s for s in self._snapshots if s.project_id == project_id]
        matching.sort(key=lambda s: s.version_number, reverse=True)
        return matching[offset : offset + limit]

    async def count_by_project_id(self, project_id: UUID) -> int:
        return sum(1 for s in self._snapshots if s.project_id == project_id)

    async def get_next_version_number(self, project_id: UUID) -> int:
        project_snapshots = [s for s in self._snapshots if s.project_id == project_id]
        if not project_snapshots:
            return 1
        return max(s.version_number for s in project_snapshots) + 1
