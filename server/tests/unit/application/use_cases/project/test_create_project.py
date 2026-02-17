from unittest.mock import AsyncMock

import pytest

from raggae.application.use_cases.project.create_project import CreateProject
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TestCreateProject:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_project_repository: AsyncMock) -> CreateProject:
        return CreateProject(project_repository=mock_project_repository)

    async def test_create_project_success(
        self,
        use_case: CreateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        from uuid import uuid4

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

    async def test_create_project_with_ingestion_settings(
        self,
        use_case: CreateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        from uuid import uuid4

        user_id = uuid4()

        # When
        result = await use_case.execute(
            user_id=user_id,
            name="My Project",
            description="A test project",
            system_prompt="You are a helpful assistant",
            chunking_strategy=ChunkingStrategy.SEMANTIC,
            parent_child_chunking=True,
        )

        # Then
        assert result.chunking_strategy == ChunkingStrategy.SEMANTIC
        assert result.parent_child_chunking is True
        mock_project_repository.save.assert_called_once()
