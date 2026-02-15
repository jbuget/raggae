from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectAlreadyPublishedError


class TestProject:
    def test_create_project_with_valid_data(self) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        now = datetime.now(UTC)

        # When
        project = Project(
            id=project_id,
            user_id=user_id,
            name="My Project",
            description="A test project",
            system_prompt="You are a helpful assistant",
            is_published=False,
            created_at=now,
        )

        # Then
        assert project.id == project_id
        assert project.user_id == user_id
        assert project.name == "My Project"
        assert project.description == "A test project"
        assert project.system_prompt == "You are a helpful assistant"
        assert project.is_published is False
        assert project.created_at == now

    def test_project_is_immutable(self) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Test",
            description="",
            system_prompt="prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )

        # When / Then
        with pytest.raises(FrozenInstanceError):
            project.name = "Changed"  # type: ignore[misc]

    def test_publish_unpublished_project(self) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Test",
            description="",
            system_prompt="prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )

        # When
        published = project.publish()

        # Then
        assert published.is_published is True
        assert published.id == project.id

    def test_publish_already_published_project_raises_error(self) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Test",
            description="",
            system_prompt="prompt",
            is_published=True,
            created_at=datetime.now(UTC),
        )

        # When / Then
        with pytest.raises(ProjectAlreadyPublishedError):
            project.publish()

    def test_update_prompt(self) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Test",
            description="",
            system_prompt="old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )

        # When
        updated = project.update_prompt("new prompt")

        # Then
        assert updated.system_prompt == "new prompt"
        assert updated.id == project.id
