from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.domain.entities.project import Project
from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


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
            chunking_strategy=ChunkingStrategy.AUTO,
            parent_child_chunking=False,
            reindex_status="idle",
            reindex_progress=0,
            reindex_total=0,
            embedding_backend="openai",
            embedding_model="text-embedding-3-small",
            embedding_api_key_encrypted="enc:super-secret",
            embedding_api_key_credential_id=uuid4(),
            org_embedding_api_key_credential_id=None,
            llm_backend="openai",
            llm_model="gpt-4.1",
            llm_api_key_encrypted="enc:other-secret",
            llm_api_key_credential_id=uuid4(),
            org_llm_api_key_credential_id=None,
            retrieval_strategy="hybrid",
            retrieval_top_k=8,
            retrieval_min_score=0.3,
            chat_history_window_size=8,
            chat_history_max_chars=4000,
            reranking_enabled=False,
            reranker_backend=None,
            reranker_model=None,
            reranker_candidate_multiplier=3,
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
        assert snapshot.chunking_strategy == sample_project.chunking_strategy
        assert snapshot.parent_child_chunking == sample_project.parent_child_chunking
        assert snapshot.embedding_backend == sample_project.embedding_backend
        assert snapshot.embedding_model == sample_project.embedding_model
        assert snapshot.embedding_api_key_credential_id == sample_project.embedding_api_key_credential_id
        assert (
            snapshot.org_embedding_api_key_credential_id == sample_project.org_embedding_api_key_credential_id
        )
        assert snapshot.llm_backend == sample_project.llm_backend
        assert snapshot.llm_model == sample_project.llm_model
        assert snapshot.llm_api_key_credential_id == sample_project.llm_api_key_credential_id
        assert snapshot.org_llm_api_key_credential_id == sample_project.org_llm_api_key_credential_id
        assert snapshot.retrieval_strategy == sample_project.retrieval_strategy
        assert snapshot.retrieval_top_k == sample_project.retrieval_top_k
        assert snapshot.retrieval_min_score == sample_project.retrieval_min_score
        assert snapshot.chat_history_window_size == sample_project.chat_history_window_size
        assert snapshot.chat_history_max_chars == sample_project.chat_history_max_chars
        assert snapshot.reranking_enabled == sample_project.reranking_enabled
        assert snapshot.reranker_backend == sample_project.reranker_backend
        assert snapshot.reranker_model == sample_project.reranker_model
        assert snapshot.reranker_candidate_multiplier == sample_project.reranker_candidate_multiplier

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
