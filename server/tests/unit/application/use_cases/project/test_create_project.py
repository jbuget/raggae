from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.project.create_project import CreateProject
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.exceptions.project_exceptions import (
    ProjectSystemPromptTooLongError,
)


class TestCreateProject:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_agent_configuration_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_organization_member_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(
        self,
        mock_project_repository: AsyncMock,
        mock_agent_configuration_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> CreateProject:
        return CreateProject(
            project_repository=mock_project_repository,
            agent_configuration_repository=mock_agent_configuration_repository,
            organization_member_repository=mock_organization_member_repository,
        )

    async def test_create_project_success(
        self,
        use_case: CreateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()

        # When
        result = await use_case.execute(
            user_id=user_id,
            name="My Project",
            description="A test project",
            system_prompt="You are a helpful assistant",
        )

        # Then
        assert result.name == "My Project"
        assert result.description == "A test project"
        assert result.system_prompt == "You are a helpful assistant"
        assert result.user_id == user_id
        assert result.is_published is False
        mock_project_repository.save.assert_called_once()

    async def test_create_project_with_too_long_system_prompt_raises(
        self,
        use_case: CreateProject,
    ) -> None:
        # Given / When / Then
        with pytest.raises(ProjectSystemPromptTooLongError):
            await use_case.execute(
                user_id=uuid4(),
                name="My Project",
                description="A test project",
                system_prompt="x" * 8001,
            )

    async def test_create_project_for_organization_requires_membership(
        self,
        use_case: CreateProject,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        mock_organization_member_repository.find_by_organization_and_user.return_value = None

        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                user_id=uuid4(),
                organization_id=uuid4(),
                name="Org Project",
                description="desc",
                system_prompt="ok",
            )

    async def test_create_project_for_organization_when_member_succeeds(
        self,
        use_case: CreateProject,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        user_id = uuid4()
        organization_id = uuid4()
        mock_organization_member_repository.find_by_organization_and_user.return_value = object()

        result = await use_case.execute(
            user_id=user_id,
            organization_id=organization_id,
            name="Org Project",
            description="desc",
            system_prompt="ok",
        )

        assert result.organization_id == organization_id

    async def test_create_project_creates_blank_agent_configuration(
        self,
        use_case: CreateProject,
        mock_agent_configuration_repository: AsyncMock,
    ) -> None:
        # Given / When
        result = await use_case.execute(
            user_id=uuid4(),
            name="My Project",
            description="desc",
            system_prompt="ok",
        )

        # Then — a blank PROJECT agent configuration should be created
        mock_agent_configuration_repository.save.assert_called_once()
        saved_config = mock_agent_configuration_repository.save.call_args.args[0]
        assert saved_config.owner_id == result.id
