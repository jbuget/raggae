from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.project_snapshot.list_project_snapshots import (
    ListProjectSnapshots,
)
from raggae.domain.entities.project import Project
from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_snapshot_repository import (
    InMemoryProjectSnapshotRepository,
)


class TestListProjectSnapshots:
    @pytest.fixture
    def project_repository(self) -> InMemoryProjectRepository:
        return InMemoryProjectRepository()

    @pytest.fixture
    def snapshot_repository(self) -> InMemoryProjectSnapshotRepository:
        return InMemoryProjectSnapshotRepository()

    @pytest.fixture
    def use_case(
        self,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
    ) -> ListProjectSnapshots:
        return ListProjectSnapshots(
            project_repository=project_repository,
            snapshot_repository=snapshot_repository,
        )

    @pytest.fixture
    def sample_project(self) -> Project:
        return Project(
            id=uuid4(),
            user_id=uuid4(),
            name="My Project",
            description="A project",
            system_prompt="You are helpful.",
            is_published=False,
            created_at=datetime.now(UTC),
            chunking_strategy=ChunkingStrategy.AUTO,
        )

    async def test_list_project_snapshots_returns_empty_when_no_snapshots(
        self,
        use_case: ListProjectSnapshots,
        project_repository: InMemoryProjectRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)

        # When
        result = await use_case.execute(
            project_id=sample_project.id,
            user_id=sample_project.user_id,
        )

        # Then
        assert result == []

    async def test_list_project_snapshots_returns_all_snapshots(
        self,
        use_case: ListProjectSnapshots,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)
        for version_number in range(1, 4):
            snapshot = ProjectSnapshot.from_project(
                project=sample_project,
                version_number=version_number,
                created_by_user_id=sample_project.user_id,
            )
            await snapshot_repository.save(snapshot)

        # When
        result = await use_case.execute(
            project_id=sample_project.id,
            user_id=sample_project.user_id,
        )

        # Then
        assert len(result) == 3

    async def test_list_project_snapshots_raises_when_project_not_found(
        self,
        use_case: ListProjectSnapshots,
    ) -> None:
        # Given
        non_existent_project_id = uuid4()
        user_id = uuid4()

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=non_existent_project_id,
                user_id=user_id,
            )

    async def test_list_project_snapshots_raises_for_unauthorized_user(
        self,
        use_case: ListProjectSnapshots,
        project_repository: InMemoryProjectRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)
        another_user_id = uuid4()

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=sample_project.id,
                user_id=another_user_id,
            )

    async def test_list_project_snapshots_supports_pagination(
        self,
        use_case: ListProjectSnapshots,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)
        for version_number in range(1, 6):
            snapshot = ProjectSnapshot.from_project(
                project=sample_project,
                version_number=version_number,
                created_by_user_id=sample_project.user_id,
            )
            await snapshot_repository.save(snapshot)

        # When
        result = await use_case.execute(
            project_id=sample_project.id,
            user_id=sample_project.user_id,
            limit=2,
            offset=0,
        )

        # Then
        assert len(result) == 2

    async def test_list_project_snapshots_returns_dtos(
        self,
        use_case: ListProjectSnapshots,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )
        await snapshot_repository.save(snapshot)

        # When
        result = await use_case.execute(
            project_id=sample_project.id,
            user_id=sample_project.user_id,
        )

        # Then
        assert len(result) == 1
        dto = result[0]
        assert dto.project_id == sample_project.id
        assert dto.version_number == 1
        assert dto.name == sample_project.name
