from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.project_snapshot.get_project_snapshot import (
    GetProjectSnapshot,
)
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.exceptions.project_snapshot_exceptions import ProjectSnapshotNotFoundError
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_organization_member_repository import (
    InMemoryOrganizationMemberRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_snapshot_repository import (
    InMemoryProjectSnapshotRepository,
)


class TestGetProjectSnapshot:
    @pytest.fixture
    def project_repository(self) -> InMemoryProjectRepository:
        return InMemoryProjectRepository()

    @pytest.fixture
    def snapshot_repository(self) -> InMemoryProjectSnapshotRepository:
        return InMemoryProjectSnapshotRepository()

    @pytest.fixture
    def org_member_repository(self) -> InMemoryOrganizationMemberRepository:
        return InMemoryOrganizationMemberRepository()

    @pytest.fixture
    def use_case(
        self,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        org_member_repository: InMemoryOrganizationMemberRepository,
    ) -> GetProjectSnapshot:
        return GetProjectSnapshot(
            project_repository=project_repository,
            snapshot_repository=snapshot_repository,
            organization_member_repository=org_member_repository,
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

    async def test_get_project_snapshot_success(
        self,
        use_case: GetProjectSnapshot,
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
            version_number=1,
            user_id=sample_project.user_id,
        )

        # Then
        assert result.project_id == sample_project.id
        assert result.version_number == 1
        assert result.name == sample_project.name

    async def test_get_project_snapshot_raises_when_project_not_found(
        self,
        use_case: GetProjectSnapshot,
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

    async def test_get_project_snapshot_raises_for_unauthorized_user(
        self,
        use_case: GetProjectSnapshot,
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

    async def test_get_project_snapshot_raises_when_version_not_found(
        self,
        use_case: GetProjectSnapshot,
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

    async def test_get_project_snapshot_returns_correct_dto_fields(
        self,
        use_case: GetProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        sample_project: Project,
    ) -> None:
        # Given
        await project_repository.save(sample_project)
        label = "stable"
        snapshot = ProjectSnapshot.from_project(
            project=sample_project,
            version_number=2,
            created_by_user_id=sample_project.user_id,
            label=label,
        )
        await snapshot_repository.save(snapshot)

        # When
        result = await use_case.execute(
            project_id=sample_project.id,
            version_number=2,
            user_id=sample_project.user_id,
        )

        # Then
        assert result.version_number == 2
        assert result.label == label
        assert result.created_by_user_id == sample_project.user_id

    async def test_get_project_snapshot_allows_org_owner(
        self,
        use_case: GetProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        org_member_repository: InMemoryOrganizationMemberRepository,
    ) -> None:
        # Given
        organization_id = uuid4()
        owner_user_id = uuid4()
        org_member_user_id = uuid4()

        org_project = Project(
            id=uuid4(),
            user_id=owner_user_id,
            organization_id=organization_id,
            name="Org Project",
            description="An org project",
            system_prompt="You are helpful.",
            is_published=False,
            created_at=datetime.now(UTC),
            chunking_strategy=ChunkingStrategy.AUTO,
        )
        await project_repository.save(org_project)

        snapshot = ProjectSnapshot.from_project(
            project=org_project,
            version_number=1,
            created_by_user_id=owner_user_id,
        )
        await snapshot_repository.save(snapshot)

        member = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=org_member_user_id,
            role=OrganizationMemberRole.OWNER,
            joined_at=datetime.now(UTC),
        )
        await org_member_repository.save(member)

        # When
        result = await use_case.execute(
            project_id=org_project.id,
            version_number=1,
            user_id=org_member_user_id,
        )

        # Then
        assert result.version_number == 1

    async def test_get_project_snapshot_allows_org_maker(
        self,
        use_case: GetProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        org_member_repository: InMemoryOrganizationMemberRepository,
    ) -> None:
        # Given
        organization_id = uuid4()
        owner_user_id = uuid4()
        maker_user_id = uuid4()

        org_project = Project(
            id=uuid4(),
            user_id=owner_user_id,
            organization_id=organization_id,
            name="Org Project",
            description="An org project",
            system_prompt="You are helpful.",
            is_published=False,
            created_at=datetime.now(UTC),
            chunking_strategy=ChunkingStrategy.AUTO,
        )
        await project_repository.save(org_project)

        snapshot = ProjectSnapshot.from_project(
            project=org_project,
            version_number=1,
            created_by_user_id=owner_user_id,
        )
        await snapshot_repository.save(snapshot)

        member = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=maker_user_id,
            role=OrganizationMemberRole.MAKER,
            joined_at=datetime.now(UTC),
        )
        await org_member_repository.save(member)

        # When
        result = await use_case.execute(
            project_id=org_project.id,
            version_number=1,
            user_id=maker_user_id,
        )

        # Then
        assert result.version_number == 1

    async def test_get_project_snapshot_allows_org_user_for_published_project(
        self,
        use_case: GetProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        org_member_repository: InMemoryOrganizationMemberRepository,
    ) -> None:
        # Given
        organization_id = uuid4()
        owner_user_id = uuid4()
        regular_user_id = uuid4()

        published_project = Project(
            id=uuid4(),
            user_id=owner_user_id,
            organization_id=organization_id,
            name="Published Project",
            description="A published project",
            system_prompt="You are helpful.",
            is_published=True,
            created_at=datetime.now(UTC),
            chunking_strategy=ChunkingStrategy.AUTO,
        )
        await project_repository.save(published_project)

        snapshot = ProjectSnapshot.from_project(
            project=published_project,
            version_number=1,
            created_by_user_id=owner_user_id,
        )
        await snapshot_repository.save(snapshot)

        member = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=regular_user_id,
            role=OrganizationMemberRole.USER,
            joined_at=datetime.now(UTC),
        )
        await org_member_repository.save(member)

        # When
        result = await use_case.execute(
            project_id=published_project.id,
            version_number=1,
            user_id=regular_user_id,
        )

        # Then
        assert result.version_number == 1

    async def test_get_project_snapshot_raises_for_org_user_on_unpublished_project(
        self,
        use_case: GetProjectSnapshot,
        project_repository: InMemoryProjectRepository,
        snapshot_repository: InMemoryProjectSnapshotRepository,
        org_member_repository: InMemoryOrganizationMemberRepository,
    ) -> None:
        # Given
        organization_id = uuid4()
        owner_user_id = uuid4()
        regular_user_id = uuid4()

        unpublished_project = Project(
            id=uuid4(),
            user_id=owner_user_id,
            organization_id=organization_id,
            name="Unpublished Project",
            description="An unpublished project",
            system_prompt="You are helpful.",
            is_published=False,
            created_at=datetime.now(UTC),
            chunking_strategy=ChunkingStrategy.AUTO,
        )
        await project_repository.save(unpublished_project)

        snapshot = ProjectSnapshot.from_project(
            project=unpublished_project,
            version_number=1,
            created_by_user_id=owner_user_id,
        )
        await snapshot_repository.save(snapshot)

        member = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=regular_user_id,
            role=OrganizationMemberRole.USER,
            joined_at=datetime.now(UTC),
        )
        await org_member_repository.save(member)

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=unpublished_project.id,
                version_number=1,
                user_id=regular_user_id,
            )
