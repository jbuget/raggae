from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.project.update_project import UpdateProject
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TestUpdateProject:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_project_repository: AsyncMock) -> UpdateProject:
        return UpdateProject(project_repository=mock_project_repository)

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

    async def test_update_project_updates_chunking_settings_when_provided(
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
            chunking_strategy=ChunkingStrategy.SEMANTIC,
            parent_child_chunking=True,
        )

        # Then
        assert result.chunking_strategy == ChunkingStrategy.SEMANTIC
        assert result.parent_child_chunking is True
