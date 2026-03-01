from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.use_cases.project.publish_project import PublishProject
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import (
    ProjectAlreadyPublishedError,
    ProjectNotFoundError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


def _make_project(
    project_id=None,
    user_id=None,
    organization_id=None,
    is_published=False,
) -> Project:
    return Project(
        id=project_id or uuid4(),
        user_id=user_id or uuid4(),
        name="Test Project",
        description="",
        system_prompt="",
        is_published=is_published,
        created_at=datetime.now(UTC),
        organization_id=organization_id,
    )


def _make_member(org_id, user_id, role: OrganizationMemberRole) -> OrganizationMember:
    return OrganizationMember(
        id=uuid4(),
        organization_id=org_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.now(UTC),
    )


class TestPublishProject:
    async def test_publish_project_as_creator_succeeds(self) -> None:
        # Given
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = project
        use_case = PublishProject(project_repository=project_repo)

        # When
        result = await use_case.execute(project_id=project.id, user_id=user_id)

        # Then
        assert result.is_published is True
        project_repo.save.assert_called_once()

    async def test_publish_project_as_org_owner_succeeds(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id)
        member = _make_member(org_id, user_id, OrganizationMemberRole.OWNER)
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = project
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = member
        use_case = PublishProject(
            project_repository=project_repo,
            organization_member_repository=org_member_repo,
        )

        # When
        result = await use_case.execute(project_id=project.id, user_id=user_id)

        # Then
        assert result.is_published is True
        project_repo.save.assert_called_once()

    async def test_publish_project_as_org_maker_succeeds(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id)
        member = _make_member(org_id, user_id, OrganizationMemberRole.MAKER)
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = project
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = member
        use_case = PublishProject(
            project_repository=project_repo,
            organization_member_repository=org_member_repo,
        )

        # When
        result = await use_case.execute(project_id=project.id, user_id=user_id)

        # Then
        assert result.is_published is True
        project_repo.save.assert_called_once()

    async def test_publish_project_as_org_user_raises_not_found(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id)
        member = _make_member(org_id, user_id, OrganizationMemberRole.USER)
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = project
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = member
        use_case = PublishProject(
            project_repository=project_repo,
            organization_member_repository=org_member_repo,
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project.id, user_id=user_id)
        project_repo.save.assert_not_called()

    async def test_publish_project_not_found_raises_error(self) -> None:
        # Given
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = None
        use_case = PublishProject(project_repository=project_repo)

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=uuid4(), user_id=uuid4())

    async def test_publish_already_published_project_raises_error(self) -> None:
        # Given
        user_id = uuid4()
        project = _make_project(user_id=user_id, is_published=True)
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = project
        use_case = PublishProject(project_repository=project_repo)

        # When / Then
        with pytest.raises(ProjectAlreadyPublishedError):
            await use_case.execute(project_id=project.id, user_id=user_id)
        project_repo.save.assert_not_called()
