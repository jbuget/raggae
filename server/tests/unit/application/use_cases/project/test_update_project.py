from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.project.update_project import UpdateProject
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import (
    ProjectNotFoundError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_snapshot_repository import (
    InMemoryProjectSnapshotRepository,
)


class TestUpdateProject:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_organization_member_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(
        self,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> UpdateProject:
        return UpdateProject(
            project_repository=mock_project_repository,
            organization_member_repository=mock_organization_member_repository,
        )

    async def test_update_project_success(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        project = Project(
            id=project_id,
            user_id=user_id,
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
        )

        # Then
        assert result.id == project_id
        assert result.user_id == user_id
        assert result.name == "New name"
        assert result.description == "New description"
        assert result.system_prompt == "New prompt"
        mock_project_repository.save.assert_called_once()

    async def test_update_project_not_found_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=uuid4(),
                user_id=uuid4(),
                name="New name",
                description="New description",
                system_prompt="New prompt",
            )

    async def test_update_project_for_other_user_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project.id,
                user_id=uuid4(),
                name="New name",
                description="New description",
                system_prompt="New prompt",
            )

    async def test_update_project_for_org_owner_is_allowed(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        organization_id = uuid4()
        requester_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=organization_id,
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_organization_member_repository.find_by_organization_and_user.return_value = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=requester_id,
            role=OrganizationMemberRole.OWNER,
            joined_at=datetime.now(UTC),
        )

        result = await use_case.execute(
            project_id=project.id,
            user_id=requester_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
        )

        assert result.name == "New name"

    async def test_update_project_for_org_maker_is_allowed(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        organization_id = uuid4()
        requester_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=organization_id,
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_organization_member_repository.find_by_organization_and_user.return_value = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=requester_id,
            role=OrganizationMemberRole.MAKER,
            joined_at=datetime.now(UTC),
        )

        result = await use_case.execute(
            project_id=project.id,
            user_id=requester_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
        )

        assert result.name == "New name"

    async def test_update_project_for_org_user_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        organization_id = uuid4()
        requester_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=organization_id,
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_organization_member_repository.find_by_organization_and_user.return_value = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=requester_id,
            role=OrganizationMemberRole.USER,
            joined_at=datetime.now(UTC),
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project.id,
                user_id=requester_id,
                name="New name",
                description="New description",
                system_prompt="New prompt",
            )

    async def test_update_project_with_too_long_system_prompt_raises_error(
        self,
        use_case: UpdateProject,
    ) -> None:
        # When / Then
        with pytest.raises(ProjectSystemPromptTooLongError):
            await use_case.execute(
                project_id=uuid4(),
                user_id=uuid4(),
                name="New name",
                description="New description",
                system_prompt="x" * 8001,
            )

    async def test_update_project_creates_snapshot_on_successful_update(self) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        project = Project(
            id=project_id,
            user_id=user_id,
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        project_repository = InMemoryProjectRepository()
        await project_repository.save(project)
        snapshot_repository = InMemoryProjectSnapshotRepository()

        use_case = UpdateProject(
            project_repository=project_repository,
            snapshot_repository=snapshot_repository,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
        )

        # Then
        count = await snapshot_repository.count_by_project_id(project_id)
        assert count == 1

    async def test_update_project_snapshot_version_increments_on_each_update(self) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        project = Project(
            id=project_id,
            user_id=user_id,
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        project_repository = InMemoryProjectRepository()
        await project_repository.save(project)
        snapshot_repository = InMemoryProjectSnapshotRepository()

        use_case = UpdateProject(
            project_repository=project_repository,
            snapshot_repository=snapshot_repository,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            name="New name 1",
            description="",
            system_prompt="",
        )
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            name="New name 2",
            description="",
            system_prompt="",
        )

        # Then
        count = await snapshot_repository.count_by_project_id(project_id)
        assert count == 2
        snapshots = await snapshot_repository.find_by_project_id(project_id)
        versions = {s.version_number for s in snapshots}
        assert versions == {1, 2}

    async def test_update_project_without_snapshot_repository_still_works(self) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        project = Project(
            id=project_id,
            user_id=user_id,
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        project_repository = InMemoryProjectRepository()
        await project_repository.save(project)

        # No snapshot_repository provided
        use_case = UpdateProject(project_repository=project_repository)

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
        )

        # Then — update works even without snapshot repo
        assert result.name == "New name"

    async def test_update_project_partial_only_system_prompt_keeps_other_fields(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        project = Project(
            id=project_id,
            user_id=user_id,
            name="Original name",
            description="Original description",
            system_prompt="Original prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When — only system_prompt is provided
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            system_prompt="Updated prompt",
        )

        # Then — name and description are preserved
        assert result.system_prompt == "Updated prompt"
        assert result.name == "Original name"
        assert result.description == "Original description"
        mock_project_repository.save.assert_called_once()
