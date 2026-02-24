from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.use_cases.project.list_projects import ListProjects
from raggae.domain.entities.project import Project


class TestListProjects:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_project_repository: AsyncMock) -> ListProjects:
        return ListProjects(project_repository=mock_project_repository)

    async def test_list_projects_returns_user_projects(
        self,
        use_case: ListProjects,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        projects = [
            Project(
                id=uuid4(),
                user_id=user_id,
                name="Project 1",
                description="desc1",
                system_prompt="prompt1",
                is_published=False,
                created_at=datetime.now(UTC),
            ),
            Project(
                id=uuid4(),
                user_id=user_id,
                name="Project 2",
                description="desc2",
                system_prompt="prompt2",
                is_published=True,
                created_at=datetime.now(UTC),
            ),
        ]
        mock_project_repository.find_by_user_id.return_value = projects

        # When
        result = await use_case.execute(user_id=user_id)

        # Then
        assert len(result) == 2
        assert result[0].name == "Project 1"
        assert result[1].name == "Project 2"

    async def test_list_projects_returns_empty_list(
        self,
        use_case: ListProjects,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_user_id.return_value = []

        # When
        result = await use_case.execute(user_id=uuid4())

        # Then
        assert result == []
