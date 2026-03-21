from typing import Protocol
from uuid import UUID

from raggae.domain.entities.project_snapshot import ProjectSnapshot


class ProjectSnapshotRepository(Protocol):
    """Interface for project snapshot persistence."""

    async def save(self, snapshot: ProjectSnapshot) -> None: ...

    async def find_by_project_and_version(
        self,
        project_id: UUID,
        version_number: int,
    ) -> ProjectSnapshot | None: ...

    async def find_by_project_id(
        self,
        project_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ProjectSnapshot]: ...

    async def count_by_project_id(self, project_id: UUID) -> int: ...

    async def get_next_version_number(self, project_id: UUID) -> int: ...
