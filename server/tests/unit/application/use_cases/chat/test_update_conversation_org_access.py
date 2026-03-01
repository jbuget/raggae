from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.chat.update_conversation import UpdateConversation
from raggae.domain.entities.conversation import Conversation
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


def _make_org_project(org_id: uuid4, is_published: bool = False) -> Project:
    return Project(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=org_id,
        name="Org project",
        description="",
        system_prompt="",
        is_published=is_published,
        created_at=datetime.now(UTC),
    )


def _make_conversation(project_id: uuid4, user_id: uuid4) -> Conversation:
    return Conversation(
        id=uuid4(),
        project_id=project_id,
        user_id=user_id,
        created_at=datetime.now(UTC),
        title="Old title",
    )


def _make_org_member_repo(org_id: uuid4, user_id: uuid4, role: OrganizationMemberRole) -> AsyncMock:
    member = OrganizationMember(
        id=uuid4(),
        organization_id=org_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.now(UTC),
    )
    repo = AsyncMock()
    repo.find_by_organization_and_user.return_value = member
    return repo


class TestUpdateConversationOrgAccess:
    async def test_owner_role_can_update_own_conversation(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_org_project(org_id)
        conversation = _make_conversation(project.id, user_id)
        project_repo = AsyncMock(find_by_id=AsyncMock(return_value=project))
        conversation_repo = AsyncMock(find_by_id=AsyncMock(return_value=conversation))
        use_case = UpdateConversation(
            project_repository=project_repo,
            conversation_repository=conversation_repo,
            organization_member_repository=_make_org_member_repo(org_id, user_id, OrganizationMemberRole.OWNER),
        )

        # When
        await use_case.execute(
            project_id=project.id,
            conversation_id=conversation.id,
            user_id=user_id,
            title="New title",
        )

        # Then
        conversation_repo.update_title.assert_awaited_once_with(conversation.id, "New title")

    async def test_maker_role_can_update_own_conversation(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_org_project(org_id)
        conversation = _make_conversation(project.id, user_id)
        project_repo = AsyncMock(find_by_id=AsyncMock(return_value=project))
        conversation_repo = AsyncMock(find_by_id=AsyncMock(return_value=conversation))
        use_case = UpdateConversation(
            project_repository=project_repo,
            conversation_repository=conversation_repo,
            organization_member_repository=_make_org_member_repo(org_id, user_id, OrganizationMemberRole.MAKER),
        )

        # When
        await use_case.execute(
            project_id=project.id,
            conversation_id=conversation.id,
            user_id=user_id,
            title="New title",
        )

        # Then
        conversation_repo.update_title.assert_awaited_once_with(conversation.id, "New title")

    async def test_user_role_published_project_can_update_own_conversation(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_org_project(org_id, is_published=True)
        conversation = _make_conversation(project.id, user_id)
        project_repo = AsyncMock(find_by_id=AsyncMock(return_value=project))
        conversation_repo = AsyncMock(find_by_id=AsyncMock(return_value=conversation))
        use_case = UpdateConversation(
            project_repository=project_repo,
            conversation_repository=conversation_repo,
            organization_member_repository=_make_org_member_repo(org_id, user_id, OrganizationMemberRole.USER),
        )

        # When
        await use_case.execute(
            project_id=project.id,
            conversation_id=conversation.id,
            user_id=user_id,
            title="New title",
        )

        # Then
        conversation_repo.update_title.assert_awaited_once_with(conversation.id, "New title")

    async def test_user_role_unpublished_project_raises(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_org_project(org_id, is_published=False)
        project_repo = AsyncMock(find_by_id=AsyncMock(return_value=project))
        use_case = UpdateConversation(
            project_repository=project_repo,
            conversation_repository=AsyncMock(),
            organization_member_repository=_make_org_member_repo(org_id, user_id, OrganizationMemberRole.USER),
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project.id,
                conversation_id=uuid4(),
                user_id=user_id,
                title="New title",
            )

    async def test_non_member_raises(self) -> None:
        # Given
        org_id = uuid4()
        project = _make_org_project(org_id)
        project_repo = AsyncMock(find_by_id=AsyncMock(return_value=project))
        member_repo = AsyncMock(find_by_organization_and_user=AsyncMock(return_value=None))
        use_case = UpdateConversation(
            project_repository=project_repo,
            conversation_repository=AsyncMock(),
            organization_member_repository=member_repo,
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project.id,
                conversation_id=uuid4(),
                user_id=uuid4(),
                title="New title",
            )
