from uuid import UUID

from raggae.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class UpdateConversation:
    """Use Case: Update conversation metadata for a user with access to the project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        conversation_repository: ConversationRepository,
        organization_member_repository: OrganizationMemberRepository | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._conversation_repository = conversation_repository
        self._organization_member_repository = organization_member_repository

    async def execute(
        self,
        project_id: UUID,
        conversation_id: UUID,
        user_id: UUID,
        title: str,
    ) -> None:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        if project.user_id != user_id:
            if project.organization_id is None or self._organization_member_repository is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
            member = await self._organization_member_repository.find_by_organization_and_user(
                organization_id=project.organization_id,
                user_id=user_id,
            )
            if member is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
            if member.role not in {OrganizationMemberRole.OWNER, OrganizationMemberRole.MAKER}:
                if not project.is_published:
                    raise ProjectNotFoundError(f"Project {project_id} not found")

        conversation = await self._conversation_repository.find_by_id(conversation_id)
        if (
            conversation is None
            or conversation.project_id != project_id
            or conversation.user_id != user_id
        ):
            raise ConversationNotFoundError(f"Conversation {conversation_id} not found")

        await self._conversation_repository.update_title(conversation_id, title)
