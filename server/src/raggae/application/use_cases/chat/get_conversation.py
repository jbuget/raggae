from uuid import UUID

from raggae.application.dto.conversation_detail_dto import ConversationDetailDTO
from raggae.application.dto.message_dto import MessageDTO
from raggae.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from raggae.application.interfaces.repositories.message_repository import MessageRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class GetConversation:
    """Use Case: Get conversation details for a user-owned project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ) -> None:
        self._project_repository = project_repository
        self._conversation_repository = conversation_repository
        self._message_repository = message_repository

    async def execute(
        self,
        project_id: UUID,
        conversation_id: UUID,
        user_id: UUID,
    ) -> ConversationDetailDTO:
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

        message_count = await self._message_repository.count_by_conversation_id(conversation.id)
        latest = await self._message_repository.find_latest_by_conversation_id(conversation.id)
        return ConversationDetailDTO(
            id=conversation.id,
            project_id=conversation.project_id,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            title=conversation.title,
            message_count=message_count,
            last_message=MessageDTO.from_entity(latest) if latest is not None else None,
        )
