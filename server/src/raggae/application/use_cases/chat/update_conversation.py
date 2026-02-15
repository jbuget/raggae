from uuid import UUID

from raggae.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class UpdateConversation:
    """Use Case: Update conversation metadata for a user-owned project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._project_repository = project_repository
        self._conversation_repository = conversation_repository

    async def execute(
        self,
        project_id: UUID,
        conversation_id: UUID,
        user_id: UUID,
        title: str,
    ) -> None:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        conversation = await self._conversation_repository.find_by_id(conversation_id)
        if (
            conversation is None
            or conversation.project_id != project_id
            or conversation.user_id != user_id
        ):
            raise ConversationNotFoundError(f"Conversation {conversation_id} not found")

        await self._conversation_repository.update_title(conversation_id, title)
