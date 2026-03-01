from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.use_cases.chat.list_conversations import ListConversations
from raggae.domain.entities.conversation import Conversation
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


def _make_project(user_id=None, organization_id=None, is_published=True) -> Project:
    return Project(
        id=uuid4(),
        user_id=user_id or uuid4(),
        name="Project",
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


class TestListConversationsOrgAccess:
    async def test_list_conversations_as_org_user_on_published_project_succeeds(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id, is_published=True)
        member = _make_member(org_id, user_id, OrganizationMemberRole.USER)
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = project
        conversation_repo = AsyncMock()
        conversation_repo.find_by_project_and_user.return_value = [
            Conversation(
                id=uuid4(),
                project_id=project.id,
                user_id=user_id,
                created_at=datetime.now(UTC),
            )
        ]
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = member
        use_case = ListConversations(
            project_repository=project_repo,
            conversation_repository=conversation_repo,
            organization_member_repository=org_member_repo,
        )

        # When
        result = await use_case.execute(project_id=project.id, user_id=user_id)

        # Then
        assert len(result) == 1

    async def test_list_conversations_as_org_user_on_unpublished_project_raises_not_found(
        self,
    ) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id, is_published=False)
        member = _make_member(org_id, user_id, OrganizationMemberRole.USER)
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = project
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = member
        use_case = ListConversations(
            project_repository=project_repo,
            conversation_repository=AsyncMock(),
            organization_member_repository=org_member_repo,
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project.id, user_id=user_id)

    async def test_list_conversations_as_org_maker_on_unpublished_project_succeeds(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id, is_published=False)
        member = _make_member(org_id, user_id, OrganizationMemberRole.MAKER)
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = project
        conversation_repo = AsyncMock()
        conversation_repo.find_by_project_and_user.return_value = []
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = member
        use_case = ListConversations(
            project_repository=project_repo,
            conversation_repository=conversation_repo,
            organization_member_repository=org_member_repo,
        )

        # When / Then (no exception)
        result = await use_case.execute(project_id=project.id, user_id=user_id)
        assert result == []

    async def test_list_conversations_non_member_raises_not_found(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id, is_published=True)
        project_repo = AsyncMock()
        project_repo.find_by_id.return_value = project
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = None
        use_case = ListConversations(
            project_repository=project_repo,
            conversation_repository=AsyncMock(),
            organization_member_repository=org_member_repo,
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project.id, user_id=user_id)
