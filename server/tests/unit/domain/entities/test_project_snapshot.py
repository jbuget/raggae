from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.domain.entities.project import Project
from raggae.domain.entities.project_snapshot import ProjectSnapshot


class TestProjectSnapshot:
    @pytest.fixture
    def sample_project(self) -> Project:
        return Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Test Project",
            description="A test project",
            system_prompt="You are a helpful assistant.",
            is_published=False,
            created_at=datetime.now(UTC),
            organization_id=None,
        )

    def test_from_project_creates_snapshot_with_correct_fields(
        self,
        sample_project: Project,
    ) -> None:
        # Given
        version_number = 1
        created_by_user_id = sample_project.user_id

        # When
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=version_number,
            created_by_user_id=created_by_user_id,
        )

        # Then
        assert snapshot.project_id == sample_project.id
        assert snapshot.version_number == version_number
        assert snapshot.created_by_user_id == created_by_user_id
        assert snapshot.label is None
        assert snapshot.restored_from_version is None

    def test_from_project_snapshots_project_fields_correctly(
        self,
        sample_project: Project,
    ) -> None:
        # Given / When
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )

        # Then — configuration fields are preserved
        assert snapshot.name == sample_project.name
        assert snapshot.description == sample_project.description
        assert snapshot.system_prompt == sample_project.system_prompt
        assert snapshot.is_published == sample_project.is_published

    def test_from_project_does_not_include_encrypted_api_keys(
        self,
        sample_project: Project,
    ) -> None:
        # Given / When
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )

        # Then — encrypted API keys are NOT part of the snapshot
        assert not hasattr(snapshot, "embedding_api_key_encrypted")
        assert not hasattr(snapshot, "llm_api_key_encrypted")

    def test_from_project_does_not_include_transient_reindex_fields(
        self,
        sample_project: Project,
    ) -> None:
        # Given / When
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )

        # Then — transient reindex fields are NOT part of the snapshot
        assert not hasattr(snapshot, "reindex_status")
        assert not hasattr(snapshot, "reindex_progress")
        assert not hasattr(snapshot, "reindex_total")

    def test_from_project_with_label(
        self,
        sample_project: Project,
    ) -> None:
        # Given
        label = "v1.0-stable"

        # When
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
            label=label,
        )

        # Then
        assert snapshot.label == label

    def test_from_project_with_restored_from_version(
        self,
        sample_project: Project,
    ) -> None:
        # Given
        restored_from = 3

        # When
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=4,
            created_by_user_id=sample_project.user_id,
            restored_from_version=restored_from,
        )

        # Then
        assert snapshot.restored_from_version == restored_from

    def test_snapshot_is_immutable(
        self,
        sample_project: Project,
    ) -> None:
        # Given
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )

        # Then
        with pytest.raises(AttributeError):
            snapshot.version_number = 99  # type: ignore[misc]

    def test_snapshot_has_unique_id(
        self,
        sample_project: Project,
    ) -> None:
        # Given / When
        snapshot1 = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )
        snapshot2 = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=2,
            created_by_user_id=sample_project.user_id,
        )

        # Then
        assert snapshot1.id != snapshot2.id

    def test_from_project_includes_organization_id(self) -> None:
        # Given
        org_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=org_id,
            name="Org Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )

        # When
        snapshot = ProjectSnapshot.from_project(
            project=project,
            version_number=1,
            created_by_user_id=project.user_id,
        )

        # Then
        assert snapshot.organization_id == org_id

    def test_from_project_snapshot_has_created_at(
        self,
        sample_project: Project,
    ) -> None:
        # Given
        before = datetime.now(UTC)

        # When
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=1,
            created_by_user_id=sample_project.user_id,
        )

        # Then
        after = datetime.now(UTC)
        assert before <= snapshot.created_at <= after
