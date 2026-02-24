from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.use_cases.project.get_project import GetProject
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class TestGetProject:
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
    ) -> GetProject:
        return GetProject(
            project_repository=mock_project_repository,
            organization_member_repository=mock_organization_member_repository,
        )

    async def test_get_project_success(
        self,
        use_case: GetProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        project = Project(
            id=project_id,
            user_id=uuid4(),
            name="My Project",
            description="desc",
            system_prompt="prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When
        result = await use_case.execute(project_id=project_id, user_id=project.user_id)

        # Then
        assert result.id == project_id
        assert result.name == "My Project"

    async def test_get_project_not_found_raises_error(
        self,
        use_case: GetProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=uuid4(), user_id=uuid4())

    async def test_get_project_other_user_raises_error(
        self,
        use_case: GetProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        owner_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=owner_id,
            name="Owner project",
            description="desc",
            system_prompt="prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project.id, user_id=uuid4())

    async def test_get_project_org_owner_can_access(
        self,
        use_case: GetProject,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        organization_id = uuid4()
        requester_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=organization_id,
            name="Org project",
            description="desc",
            system_prompt="prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_organization_member_repository.find_by_organization_and_user.return_value = (
            OrganizationMember(
                id=uuid4(),
                organization_id=organization_id,
                user_id=requester_id,
                role=OrganizationMemberRole.OWNER,
                joined_at=datetime.now(UTC),
            )
        )

        result = await use_case.execute(project_id=project.id, user_id=requester_id)

        assert result.id == project.id

    async def test_get_project_org_maker_can_access(
        self,
        use_case: GetProject,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        organization_id = uuid4()
        requester_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=organization_id,
            name="Org project",
            description="desc",
            system_prompt="prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_organization_member_repository.find_by_organization_and_user.return_value = (
            OrganizationMember(
                id=uuid4(),
                organization_id=organization_id,
                user_id=requester_id,
                role=OrganizationMemberRole.MAKER,
                joined_at=datetime.now(UTC),
            )
        )

        result = await use_case.execute(project_id=project.id, user_id=requester_id)

        assert result.id == project.id

    async def test_get_project_org_user_cannot_access(
        self,
        use_case: GetProject,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        organization_id = uuid4()
        requester_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=organization_id,
            name="Org project",
            description="desc",
            system_prompt="prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_organization_member_repository.find_by_organization_and_user.return_value = (
            OrganizationMember(
                id=uuid4(),
                organization_id=organization_id,
                user_id=requester_id,
                role=OrganizationMemberRole.USER,
                joined_at=datetime.now(UTC),
            )
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project.id, user_id=requester_id)
