from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.project_snapshot.restore_project_snapshot import (
    RestoreProjectSnapshot,
)
from raggae.domain.entities.project import Project
from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.exceptions.project_snapshot_exceptions import ProjectSnapshotNotFoundError
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_snapshot_repository import (
    InMemoryProjectSnapshotRepository,
)


class TestRestoreProjectSnapshot:
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
    ) -> RestoreProjectSnapshot:
        return RestoreProjectSnapshot(
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
            retrieval_strategy="hybrid",
            retrieval_top_k=8,
            retrieval_min_score=0.3,
            chat_history_window_size=8,
            chat_history_max_chars=4000,
            reranking_enabled=False,
            reranker_candidate_multiplier=3,
        )

    async def test_restore_project_snapshot_applies_snapshot_fields_to_project(
        self,
        use_case: RestoreProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given — a snapshot with different values
        original_name = "Original name"
        original_system_prompt = "Original prompt"
        snapshot = ProjectSnapshot.from_project(
            project=Project(
                id=sample_project.id,
                user_id=sample_project.user_id,
                name=original_name,
                description="Original description",
                system_prompt=original_system_prompt,
                is_published=False,
                created_at=datetime.now(UTC),
                chunking_strategy=ChunkingStrategy.AUTO,
                retrieval_strategy="hybrid",
                retrieval_top_k=8,
                retrieval_min_score=0.3,
                chat_history_window_size=8,
                chat_history_max_chars=4000,
                reranking_enabled=False,
                reranker_candidate_multiplier=3,
            ),
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )
        await snapshot_repository.save(snapshot)

        # Update the project so it differs from the snapshot
        updated_project = Project(
            id=sample_project.id,
            user_id=sample_project.user_id,
            name="Updated name",
            description="Updated description",
            system_prompt="Updated prompt",
            is_published=False,
            created_at=sample_project.created_at,
            chunking_strategy=ChunkingStrategy.AUTO,
            retrieval_strategy="hybrid",
            retrieval_top_k=8,
            retrieval_min_score=0.3,
            chat_history_window_size=8,
            chat_history_max_chars=4000,
            reranking_enabled=False,
            reranker_candidate_multiplier=3,
        )
        await project_repository.save(updated_project)

        # When
        result_dto = await use_case.execute(
            project_id=sample_project.id,
            version_number=1,
            user_id=sample_project.user_id,
        )

        # Then — result reflects restored snapshot values
        assert result_dto.name == original_name
        assert result_dto.system_prompt == original_system_prompt

    async def test_restore_project_snapshot_creates_new_snapshot_with_restored_from_version(
        self,
        use_case: RestoreProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )
        await snapshot_repository.save(snapshot)
        await project_repository.save(sample_project)

        # When
        await use_case.execute(
            project_id=sample_project.id,
            version_number=1,
            user_id=sample_project.user_id,
        )

        # Then — a new snapshot is created with restored_from_version set
        count = await snapshot_repository.count_by_project_id(sample_project.id)
        assert count == 2  # original + the restored one

        new_snapshot = await snapshot_repository.find_by_project_and_version(
            project_id=sample_project.id,
            version_number=2,
        )
        assert new_snapshot is not None
        assert new_snapshot.restored_from_version == 1

    async def test_restore_project_snapshot_raises_when_project_not_found(
        self,
        use_case: RestoreProjectSnapshot,
    ) -> None:
        # Given
        non_existent_project_id = uuid4()
        user_id = uuid4()

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=non_existent_project_id,
                version_number=1,
                user_id=user_id,
            )

    async def test_restore_project_snapshot_raises_for_unauthorized_user(
        self,
        use_case: RestoreProjectSnapshot,
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
                version_number=1,
                user_id=another_user_id,
            )

    async def test_restore_project_snapshot_raises_when_version_not_found(
        self,
        use_case: RestoreProjectSnapshot,
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

        # When / Then
        with pytest.raises(ProjectSnapshotNotFoundError):
            await use_case.execute(
                project_id=sample_project.id,
                version_number=99,
                user_id=sample_project.user_id,
            )

    async def test_restore_project_snapshot_returns_project_dto(
        self,
        use_case: RestoreProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )
        await snapshot_repository.save(snapshot)
        await project_repository.save(sample_project)

        # When
        result_dto = await use_case.execute(
            project_id=sample_project.id,
            version_number=1,
            user_id=sample_project.user_id,
        )

        # Then
        assert result_dto.id == sample_project.id
        assert result_dto.name == sample_project.name
