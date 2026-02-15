from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.chat_message_response_dto import ChatMessageResponseDTO
from raggae.application.dto.chat_stream_event import (
    ChatStreamDone,
    ChatStreamEvent,
    ChatStreamToken,
)
from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from raggae.application.interfaces.repositories.message_repository import MessageRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.chat_security_policy import ChatSecurityPolicy
from raggae.application.interfaces.services.conversation_title_generator import (
    ConversationTitleGenerator,
)
from raggae.application.interfaces.services.llm_service import LLMService
from raggae.application.services.chat_security_policy import StaticChatSecurityPolicy
from raggae.application.use_cases.chat.query_relevant_chunks import QueryRelevantChunks
from raggae.domain.entities.conversation import Conversation
from raggae.domain.entities.message import Message
from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError
from raggae.domain.exceptions.document_exceptions import LLMGenerationError


class SendMessage:
    """Use Case: Generate an answer from a user message and retrieved chunks."""

    def __init__(
        self,
        query_relevant_chunks_use_case: QueryRelevantChunks,
        llm_service: LLMService,
        conversation_title_generator: ConversationTitleGenerator,
        project_repository: ProjectRepository,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        chat_security_policy: ChatSecurityPolicy | None = None,
        default_chunk_limit: int = 8,
        max_chunk_limit: int = 40,
        history_window_size: int = 8,
        history_max_chars: int = 4000,
    ) -> None:
        self._query_relevant_chunks_use_case = query_relevant_chunks_use_case
        self._llm_service = llm_service
        self._conversation_title_generator = conversation_title_generator
        self._project_repository = project_repository
        self._conversation_repository = conversation_repository
        self._message_repository = message_repository
        self._default_chunk_limit = max(1, default_chunk_limit)
        self._max_chunk_limit = max(1, max_chunk_limit)
        self._history_window_size = max(1, history_window_size)
        self._history_max_chars = max(128, history_max_chars)
        if chat_security_policy is None:
            self._chat_security_policy: ChatSecurityPolicy = StaticChatSecurityPolicy()
        else:
            self._chat_security_policy = chat_security_policy

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        message: str,
        limit: int | None = None,
        offset: int = 0,
        conversation_id: UUID | None = None,
        start_new_conversation: bool = False,
        retrieval_strategy: str = "hybrid",
        retrieval_filters: dict[str, object] | None = None,
    ) -> ChatMessageResponseDTO:
        effective_limit = self._resolve_effective_chunk_limit(
            message=message,
            requested_limit=limit,
            retrieval_strategy=retrieval_strategy,
        )
        is_new_conversation = conversation_id is None
        skip_user_message_save = False
        current_user_message_id: UUID | None = None
        if is_new_conversation:
            conversation, skip_user_message_save = await self._get_or_create_pending_conversation(
                project_id=project_id,
                user_id=user_id,
                message=message,
                start_new_conversation=start_new_conversation,
            )
        else:
            conversation = await self._conversation_repository.find_by_id(conversation_id)
            if (
                conversation is None
                or conversation.project_id != project_id
                or conversation.user_id != user_id
            ):
                raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
        if not skip_user_message_save:
            current_user_message_id = uuid4()
            await self._message_repository.save(
                Message(
                    id=current_user_message_id,
                    conversation_id=conversation.id,
                    role="user",
                    content=message,
                    created_at=datetime.now(UTC),
                )
            )
        if self._chat_security_policy.is_disallowed_user_message(message):
            refusal_answer = (
                "I cannot disclose system or internal instructions. "
                "I can help with project content or answer your business question instead."
            )
            await self._message_repository.save(
                Message(
                    id=uuid4(),
                    conversation_id=conversation.id,
                    role="assistant",
                    content=refusal_answer,
                    source_documents=[],
                    reliability_percent=0,
                    created_at=datetime.now(UTC),
                )
            )
            if is_new_conversation:
                title = await self._build_conversation_title(
                    user_message=message,
                    assistant_answer=refusal_answer,
                )
                await self._conversation_repository.update_title(conversation.id, title)
            return ChatMessageResponseDTO(
                project_id=project_id,
                conversation_id=conversation.id,
                message=message,
                answer=refusal_answer,
                chunks=[],
                history_messages_used=0,
                chunks_used=0,
            )
        retrieval_result = await self._query_relevant_chunks_use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query=message,
            limit=effective_limit,
            offset=offset,
            strategy=retrieval_strategy,
            metadata_filters=retrieval_filters,
        )
        relevant_chunks = self._select_useful_chunks(
            self._filter_relevant_chunks(retrieval_result.chunks),
            effective_limit,
        )
        if not relevant_chunks:
            fallback_answer = "I could not find relevant context to answer your message."
            await self._message_repository.save(
                Message(
                    id=uuid4(),
                    conversation_id=conversation.id,
                    role="assistant",
                    content=fallback_answer,
                    source_documents=[],
                    reliability_percent=0,
                    created_at=datetime.now(UTC),
                )
            )
            if is_new_conversation:
                title = await self._build_conversation_title(
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
                retrieval_strategy_used=retrieval_result.strategy_used,
                retrieval_execution_time_ms=retrieval_result.execution_time_ms,
                history_messages_used=0,
                chunks_used=0,
            )
        project = await self._project_repository.find_by_id(project_id)
        project_system_prompt = project.system_prompt if project is not None else None
        conversation_history = await self._build_conversation_history(
            conversation_id=conversation.id,
            current_user_message_id=current_user_message_id,
        )
        try:
            answer = await self._llm_service.generate_answer(
                query=message,
                context_chunks=[chunk.content for chunk in relevant_chunks],
                project_system_prompt=project_system_prompt,
                conversation_history=conversation_history,
            )
            sanitized_answer = self._chat_security_policy.sanitize_model_answer(answer)
            if sanitized_answer != answer:
                answer = sanitized_answer
                source_documents = []
                reliability_percent = 0
            else:
                source_documents = self._extract_source_documents(relevant_chunks)
                reliability_percent = self._compute_reliability_percent(relevant_chunks)
        except LLMGenerationError:
            answer = (
                "I found relevant context but could not generate an answer right now. "
                "Please try again in a few seconds."
            )
            source_documents = []
            reliability_percent = 0
        await self._message_repository.save(
            Message(
                id=uuid4(),
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
                source_documents=source_documents,
                reliability_percent=reliability_percent,
                created_at=datetime.now(UTC),
            )
        )
        if is_new_conversation:
            title = await self._build_conversation_title(
                user_message=message,
                assistant_answer=answer,
            )
            await self._conversation_repository.update_title(conversation.id, title)
        return ChatMessageResponseDTO(
            project_id=project_id,
            conversation_id=conversation.id,
            message=message,
            answer=answer,
            chunks=relevant_chunks,
            retrieval_strategy_used=retrieval_result.strategy_used,
            retrieval_execution_time_ms=retrieval_result.execution_time_ms,
            history_messages_used=len(conversation_history),
            chunks_used=len(relevant_chunks),
        )

    async def execute_stream(
        self,
        project_id: UUID,
        user_id: UUID,
        message: str,
        limit: int | None = None,
        offset: int = 0,
        conversation_id: UUID | None = None,
        start_new_conversation: bool = False,
        retrieval_strategy: str = "hybrid",
        retrieval_filters: dict[str, object] | None = None,
    ) -> AsyncIterator[ChatStreamEvent]:
        effective_limit = self._resolve_effective_chunk_limit(
            message=message,
            requested_limit=limit,
            retrieval_strategy=retrieval_strategy,
        )
        is_new_conversation = conversation_id is None
        skip_user_message_save = False
        current_user_message_id: UUID | None = None
        if is_new_conversation:
            conversation, skip_user_message_save = await self._get_or_create_pending_conversation(
                project_id=project_id,
                user_id=user_id,
                message=message,
                start_new_conversation=start_new_conversation,
            )
        else:
            conversation = await self._conversation_repository.find_by_id(conversation_id)
            if (
                conversation is None
                or conversation.project_id != project_id
                or conversation.user_id != user_id
            ):
                raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
        if not skip_user_message_save:
            current_user_message_id = uuid4()
            await self._message_repository.save(
                Message(
                    id=current_user_message_id,
                    conversation_id=conversation.id,
                    role="user",
                    content=message,
                    created_at=datetime.now(UTC),
                )
            )
        if self._chat_security_policy.is_disallowed_user_message(message):
            refusal_answer = (
                "I cannot disclose system or internal instructions. "
                "I can help with project content or answer your business question instead."
            )
            await self._message_repository.save(
                Message(
                    id=uuid4(),
                    conversation_id=conversation.id,
                    role="assistant",
                    content=refusal_answer,
                    source_documents=[],
                    reliability_percent=0,
                    created_at=datetime.now(UTC),
                )
            )
            if is_new_conversation:
                title = await self._build_conversation_title(
                    user_message=message,
                    assistant_answer=refusal_answer,
                )
                await self._conversation_repository.update_title(conversation.id, title)
            yield ChatStreamToken(token=refusal_answer)
            yield ChatStreamDone(
                conversation_id=conversation.id,
                answer=refusal_answer,
                chunks=[],
                history_messages_used=0,
                chunks_used=0,
            )
            return
        retrieval_result = await self._query_relevant_chunks_use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query=message,
            limit=effective_limit,
            offset=offset,
            strategy=retrieval_strategy,
            metadata_filters=retrieval_filters,
        )
        relevant_chunks = self._select_useful_chunks(
            self._filter_relevant_chunks(retrieval_result.chunks),
            effective_limit,
        )
        if not relevant_chunks:
            fallback_answer = "I could not find relevant context to answer your message."
            await self._message_repository.save(
                Message(
                    id=uuid4(),
                    conversation_id=conversation.id,
                    role="assistant",
                    content=fallback_answer,
                    source_documents=[],
                    reliability_percent=0,
                    created_at=datetime.now(UTC),
                )
            )
            if is_new_conversation:
                title = await self._build_conversation_title(
                    user_message=message,
                    assistant_answer=fallback_answer,
                )
                await self._conversation_repository.update_title(conversation.id, title)
            yield ChatStreamToken(token=fallback_answer)
            yield ChatStreamDone(
                conversation_id=conversation.id,
                answer=fallback_answer,
                chunks=[],
                retrieval_strategy_used=retrieval_result.strategy_used,
                retrieval_execution_time_ms=retrieval_result.execution_time_ms,
                history_messages_used=0,
                chunks_used=0,
            )
            return
        project = await self._project_repository.find_by_id(project_id)
        project_system_prompt = project.system_prompt if project is not None else None
        conversation_history = await self._build_conversation_history(
            conversation_id=conversation.id,
            current_user_message_id=current_user_message_id,
        )
        accumulated_answer = ""
        try:
            stream = self._llm_service.generate_answer_stream(
                query=message,
                context_chunks=[chunk.content for chunk in relevant_chunks],
                project_system_prompt=project_system_prompt,
                conversation_history=conversation_history,
            )
            async for token in stream:
                accumulated_answer += token
                yield ChatStreamToken(token=token)
            sanitized = self._chat_security_policy.sanitize_model_answer(accumulated_answer)
            if sanitized != accumulated_answer:
                accumulated_answer = sanitized
                source_documents: list[dict[str, object]] = []
                reliability_percent = 0
            else:
                source_documents = self._extract_source_documents(relevant_chunks)
                reliability_percent = self._compute_reliability_percent(relevant_chunks)
        except LLMGenerationError:
            accumulated_answer = (
                "I found relevant context but could not generate an answer right now. "
                "Please try again in a few seconds."
            )
            source_documents = []
            reliability_percent = 0
        await self._message_repository.save(
            Message(
                id=uuid4(),
                conversation_id=conversation.id,
                role="assistant",
                content=accumulated_answer,
                source_documents=source_documents,
                reliability_percent=reliability_percent,
                created_at=datetime.now(UTC),
            )
        )
        if is_new_conversation:
            title = await self._build_conversation_title(
                user_message=message,
                assistant_answer=accumulated_answer,
            )
            await self._conversation_repository.update_title(conversation.id, title)
        yield ChatStreamDone(
            conversation_id=conversation.id,
            answer=accumulated_answer,
            chunks=relevant_chunks,
            retrieval_strategy_used=retrieval_result.strategy_used,
            retrieval_execution_time_ms=retrieval_result.execution_time_ms,
            history_messages_used=len(conversation_history),
            chunks_used=len(relevant_chunks),
        )

    async def _build_conversation_title(self, user_message: str, assistant_answer: str) -> str:
        fallback = self._normalize_title(user_message)
        try:
            generated = await self._conversation_title_generator.generate_title(
                user_message=user_message,
                assistant_answer=assistant_answer,
            )
        except Exception:
            return fallback
        normalized = self._normalize_title(generated)
        if not normalized:
            return fallback
        return normalized

    def _normalize_title(self, value: str) -> str:
        return value.strip()[: self._MAX_CONVERSATION_TITLE_LENGTH].strip()

    def _extract_source_documents(self, chunks: list[RetrievedChunkDTO]) -> list[dict[str, object]]:
        unique: dict[str, dict[str, object]] = {}
        for chunk in chunks:
            key = str(chunk.document_id)
            if key not in unique:
                payload: dict[str, object] = {"document_id": key, "chunk_ids": []}
                if chunk.document_file_name is not None:
                    payload["document_file_name"] = chunk.document_file_name
                unique[key] = payload
            chunk_ids = unique[key]["chunk_ids"]
            if isinstance(chunk_ids, list):
                chunk_ids.append(str(chunk.chunk_id))
        return list(unique.values())

    def _compute_reliability_percent(self, chunks: list[RetrievedChunkDTO]) -> int:
        if not chunks:
            return 0
        average_score = sum(chunk.score for chunk in chunks) / len(chunks)
        bounded = min(max(average_score, 0.0), 1.0)
        return int(round(bounded * 100))

    def _filter_relevant_chunks(self, chunks: list[RetrievedChunkDTO]) -> list[RetrievedChunkDTO]:
        return [chunk for chunk in chunks if chunk.score > 0.0 and chunk.content.strip()]

    def _resolve_effective_chunk_limit(
        self,
        message: str,
        requested_limit: int | None,
        retrieval_strategy: str,
    ) -> int:
        if requested_limit is not None:
            return max(1, min(requested_limit, self._max_chunk_limit))
        words = len(message.split())
        if retrieval_strategy == "fulltext":
            base = 6
        elif words > 20:
            base = 12
        elif words > 8:
            base = 10
        else:
            base = self._default_chunk_limit
        return max(1, min(base, self._max_chunk_limit))

    def _select_useful_chunks(
        self,
        chunks: list[RetrievedChunkDTO],
        limit: int,
    ) -> list[RetrievedChunkDTO]:
        if len(chunks) <= limit:
            return chunks
        selected: list[RetrievedChunkDTO] = []
        seen_documents: set[UUID] = set()
        for chunk in chunks:
            if chunk.document_id in seen_documents:
                continue
            selected.append(chunk)
            seen_documents.add(chunk.document_id)
            if len(selected) == limit:
                return selected
        for chunk in chunks:
            if chunk in selected:
                continue
            selected.append(chunk)
            if len(selected) == limit:
                break
        return selected

    async def _get_or_create_pending_conversation(
        self,
        project_id: UUID,
        user_id: UUID,
        message: str,
        start_new_conversation: bool,
    ) -> tuple[Conversation, bool]:
        if start_new_conversation:
            created = await self._conversation_repository.create(
                project_id=project_id,
                user_id=user_id,
            )
            return created, False
        latest_candidates = await self._conversation_repository.find_by_project_and_user(
            project_id=project_id,
            user_id=user_id,
            limit=1,
            offset=0,
        )
        if not latest_candidates:
            created = await self._conversation_repository.create(
                project_id=project_id,
                user_id=user_id,
            )
            return created, False

        latest = latest_candidates[0]
        latest_message = await self._message_repository.find_latest_by_conversation_id(latest.id)
        if (
            latest_message is not None
            and latest_message.role == "user"
            and latest_message.content == message
        ):
            return latest, True
        return latest, False

    async def _build_conversation_history(
        self,
        conversation_id: UUID,
        current_user_message_id: UUID | None,
    ) -> list[str]:
        total_messages = await self._message_repository.count_by_conversation_id(conversation_id)
        offset = max(0, total_messages - self._history_window_size)
        messages = await self._message_repository.find_by_conversation_id(
            conversation_id=conversation_id,
            limit=self._history_window_size,
            offset=offset,
        )
        history: list[str] = []
        for message in messages:
            if current_user_message_id is not None and message.id == current_user_message_id:
                continue
            label = "User" if message.role == "user" else "Assistant"
            history.append(f"{label}: {message.content}")
        return self._truncate_history_by_chars(history[-self._history_window_size :])

    def _truncate_history_by_chars(self, history: list[str]) -> list[str]:
        total_chars = sum(len(item) for item in history)
        if total_chars <= self._history_max_chars:
            return history
        trimmed = history[:]
        while trimmed and total_chars > self._history_max_chars:
            removed = trimmed.pop(0)
            total_chars -= len(removed)
        return trimmed

    _MAX_CONVERSATION_TITLE_LENGTH = 80
