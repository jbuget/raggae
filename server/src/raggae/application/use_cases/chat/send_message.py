from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.chat_message_response_dto import ChatMessageResponseDTO
from raggae.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from raggae.application.interfaces.repositories.message_repository import MessageRepository
from raggae.application.interfaces.services.conversation_title_generator import (
    ConversationTitleGenerator,
)
from raggae.application.interfaces.services.llm_service import LLMService
from raggae.application.use_cases.chat.query_relevant_chunks import QueryRelevantChunks
from raggae.domain.entities.message import Message
from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError


class SendMessage:
    """Use Case: Generate an answer from a user message and retrieved chunks."""

    def __init__(
        self,
        query_relevant_chunks_use_case: QueryRelevantChunks,
        llm_service: LLMService,
        conversation_title_generator: ConversationTitleGenerator,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ) -> None:
        self._query_relevant_chunks_use_case = query_relevant_chunks_use_case
        self._llm_service = llm_service
        self._conversation_title_generator = conversation_title_generator
        self._conversation_repository = conversation_repository
        self._message_repository = message_repository

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        message: str,
        limit: int = 5,
        conversation_id: UUID | None = None,
    ) -> ChatMessageResponseDTO:
        is_new_conversation = conversation_id is None
        if is_new_conversation:
            conversation = await self._conversation_repository.get_or_create(
                project_id=project_id,
                user_id=user_id,
            )
        else:
            conversation = await self._conversation_repository.find_by_id(conversation_id)
            if (
                conversation is None
                or conversation.project_id != project_id
                or conversation.user_id != user_id
            ):
                raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
        await self._message_repository.save(
            Message(
                id=uuid4(),
                conversation_id=conversation.id,
                role="user",
                content=message,
                created_at=datetime.now(UTC),
            )
        )
        chunks = await self._query_relevant_chunks_use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query=message,
            limit=limit,
        )
        if not chunks:
            fallback_answer = "I could not find relevant context to answer your message."
            await self._message_repository.save(
                Message(
                    id=uuid4(),
                    conversation_id=conversation.id,
                    role="assistant",
                    content=fallback_answer,
                    created_at=datetime.now(UTC),
                )
            )
            if is_new_conversation:
                title = await self._conversation_title_generator.generate_title(
                    user_message=message,
                    assistant_answer=fallback_answer,
                )
                await self._conversation_repository.update_title(conversation.id, title)
            return ChatMessageResponseDTO(
                project_id=project_id,
                conversation_id=conversation.id,
                message=message,
                answer=fallback_answer,
                chunks=[],
            )
        answer = await self._llm_service.generate_answer(
            query=message,
            context_chunks=[chunk.content for chunk in chunks],
        )
        await self._message_repository.save(
            Message(
                id=uuid4(),
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
                created_at=datetime.now(UTC),
            )
        )
        if is_new_conversation:
            title = await self._conversation_title_generator.generate_title(
                user_message=message,
                assistant_answer=answer,
            )
            await self._conversation_repository.update_title(conversation.id, title)
        return ChatMessageResponseDTO(
            project_id=project_id,
            conversation_id=conversation.id,
            message=message,
            answer=answer,
            chunks=chunks,
        )
