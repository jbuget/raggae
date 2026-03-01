from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.dto.query_relevant_chunks_result_dto import QueryRelevantChunksResultDTO
from raggae.application.use_cases.chat.send_message import SendMessage
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


def _make_use_case(project: Project, org_member_repo=None) -> SendMessage:
    query_use_case = AsyncMock()
    query_use_case.execute.return_value = QueryRelevantChunksResultDTO(
        chunks=[], strategy_used="hybrid", execution_time_ms=1.0
    )
    llm_service = AsyncMock()
    llm_service.generate_answer.return_value = "answer"
    conversation_repository = AsyncMock()
    conversation_repository.find_by_project_and_user.return_value = []
    conversation_repository.create.return_value = Conversation(
        id=uuid4(),
        project_id=project.id,
        user_id=uuid4(),
        created_at=datetime.now(UTC),
    )
    message_repository = AsyncMock()
    message_repository.count_by_conversation_id.return_value = 0
    message_repository.find_by_conversation_id.return_value = []
    project_repository = AsyncMock()
    project_repository.find_by_id.return_value = project
    title_generator = AsyncMock()
    title_generator.generate_title.return_value = "Title"
    return SendMessage(
        query_relevant_chunks_use_case=query_use_case,
        llm_service=llm_service,
        conversation_title_generator=title_generator,
        project_repository=project_repository,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        organization_member_repository=org_member_repo,
    )


class TestSendMessageOrgAccess:
    async def test_send_message_as_org_user_on_published_project_succeeds(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id, is_published=True)
        member = _make_member(org_id, user_id, OrganizationMemberRole.USER)
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = member
        use_case = _make_use_case(project, org_member_repo)

        # When / Then (no exception)
        result = await use_case.execute(
            project_id=project.id,
            user_id=user_id,
            message="hello",
        )
        assert result is not None

    async def test_send_message_as_org_user_on_unpublished_project_raises_not_found(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id, is_published=False)
        member = _make_member(org_id, user_id, OrganizationMemberRole.USER)
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = member
        use_case = _make_use_case(project, org_member_repo)

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project.id,
                user_id=user_id,
                message="hello",
            )

    async def test_send_message_as_org_maker_on_unpublished_project_succeeds(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id, is_published=False)
        member = _make_member(org_id, user_id, OrganizationMemberRole.MAKER)
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = member
        use_case = _make_use_case(project, org_member_repo)

        # When / Then (no exception)
        result = await use_case.execute(
            project_id=project.id,
            user_id=user_id,
            message="hello",
        )
        assert result is not None

    async def test_send_message_as_non_member_raises_not_found(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        project = _make_project(organization_id=org_id, is_published=True)
        org_member_repo = AsyncMock()
        org_member_repo.find_by_organization_and_user.return_value = None
        use_case = _make_use_case(project, org_member_repo)

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project.id,
                user_id=user_id,
                message="hello",
            )
