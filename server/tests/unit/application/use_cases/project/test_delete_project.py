from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.project.delete_project import DeleteProject
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestDeleteProject:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_project_repository: AsyncMock) -> DeleteProject:
        return DeleteProject(project_repository=mock_project_repository)

    async def test_delete_project_success(
        self,
        use_case: DeleteProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        project = Project(
            id=project_id,
            user_id=uuid4(),
            name="To Delete",
            description="",
            system_prompt="prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When
        await use_case.execute(project_id=project_id)

        # Then
        mock_project_repository.delete.assert_called_once_with(project_id)

    async def test_delete_project_not_found_raises_error(
        self,
        use_case: DeleteProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=uuid4())
