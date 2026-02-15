from uuid import UUID

from raggae.application.dto.conversation_dto import ConversationDTO
from raggae.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class ListConversations:
    """Use Case: List conversations for a user-owned project."""

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
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ConversationDTO]:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        conversations = await self._conversation_repository.find_by_project_and_user(
            project_id=project_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        return [ConversationDTO.from_entity(conversation) for conversation in conversations]
