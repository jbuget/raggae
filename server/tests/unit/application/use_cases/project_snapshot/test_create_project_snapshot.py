from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.project_snapshot.create_project_snapshot import (
    CreateProjectSnapshot,
)
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_snapshot_repository import (
    InMemoryProjectSnapshotRepository,
)


class TestCreateProjectSnapshot:
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
    ) -> CreateProjectSnapshot:
        return CreateProjectSnapshot(
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

    async def test_create_project_snapshot_success(
        self,
        use_case: CreateProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)
        user_id = sample_project.user_id

        # When
        snapshot_dto = await use_case.execute(
            project_id=sample_project.id,
            created_by_user_id=user_id,
        )

        # Then
        assert snapshot_dto.project_id == sample_project.id
        assert snapshot_dto.version_number == 1
        assert snapshot_dto.created_by_user_id == user_id
        assert snapshot_dto.label is None
        assert snapshot_dto.restored_from_version is None

    async def test_create_project_snapshot_version_increments_sequentially(
        self,
        use_case: CreateProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)
        user_id = sample_project.user_id

        # When
        snapshot1 = await use_case.execute(
            project_id=sample_project.id,
            created_by_user_id=user_id,
        )
        snapshot2 = await use_case.execute(
            project_id=sample_project.id,
            created_by_user_id=user_id,
        )
        snapshot3 = await use_case.execute(
            project_id=sample_project.id,
            created_by_user_id=user_id,
        )

        # Then
        assert snapshot1.version_number == 1
        assert snapshot2.version_number == 2
        assert snapshot3.version_number == 3

    async def test_create_project_snapshot_with_label(
        self,
        use_case: CreateProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)
        label = "release-1.0"

        # When
        snapshot_dto = await use_case.execute(
            project_id=sample_project.id,
            created_by_user_id=sample_project.user_id,
            label=label,
        )

        # Then
        assert snapshot_dto.label == label

    async def test_create_project_snapshot_with_restored_from_version(
        self,
        use_case: CreateProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)

        # When
        snapshot_dto = await use_case.execute(
            project_id=sample_project.id,
            created_by_user_id=sample_project.user_id,
            restored_from_version=3,
        )

        # Then
        assert snapshot_dto.restored_from_version == 3

    async def test_create_project_snapshot_raises_when_project_not_found(
        self,
        use_case: CreateProjectSnapshot,
    ) -> None:
        # Given
        non_existent_project_id = uuid4()
        user_id = uuid4()

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=non_existent_project_id,
                created_by_user_id=user_id,
            )

    async def test_create_project_snapshot_persists_snapshot(
        self,
        use_case: CreateProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)

        # When
        await use_case.execute(
            project_id=sample_project.id,
            created_by_user_id=sample_project.user_id,
        )

        # Then
        count = await snapshot_repository.count_by_project_id(sample_project.id)
        assert count == 1

    async def test_create_project_snapshot_preserves_project_config(
        self,
        use_case: CreateProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)

        # When
        snapshot_dto = await use_case.execute(
            project_id=sample_project.id,
            created_by_user_id=sample_project.user_id,
        )

        # Then
        assert snapshot_dto.name == sample_project.name
        assert snapshot_dto.description == sample_project.description
        assert snapshot_dto.system_prompt == sample_project.system_prompt
        assert snapshot_dto.is_published == sample_project.is_published
