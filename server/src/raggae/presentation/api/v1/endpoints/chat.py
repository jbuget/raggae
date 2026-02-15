import json
import logging
from collections.abc import AsyncIterator
from time import perf_counter
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from raggae.application.use_cases.chat.delete_conversation import DeleteConversation
from raggae.application.use_cases.chat.get_conversation import GetConversation
from raggae.application.use_cases.chat.list_conversation_messages import (
    ListConversationMessages,
)
from raggae.application.use_cases.chat.list_conversations import ListConversations
from raggae.application.use_cases.chat.send_message import SendMessage
from raggae.application.use_cases.chat.update_conversation import UpdateConversation
from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError
from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.infrastructure.config.settings import settings
from raggae.presentation.api.dependencies import (
    get_current_user_id,
    get_delete_conversation_use_case,
    get_get_conversation_use_case,
    get_list_conversation_messages_use_case,
    get_list_conversations_use_case,
    get_send_message_use_case,
    get_update_conversation_use_case,
)
from raggae.presentation.api.v1.schemas.chat_schemas import (
    ConversationDetailResponse,
    ConversationResponse,
    MessageResponse,
    SendMessageRequest,
    SendMessageResponse,
    UpdateConversationRequest,
)
from raggae.presentation.api.v1.schemas.query_schemas import RetrievedChunkResponse

router = APIRouter(
    prefix="/projects/{project_id}/chat",
    tags=["chat"],
    dependencies=[Depends(get_current_user_id)],
)
logger = logging.getLogger(__name__)


@router.post("/messages")
async def send_message(
    project_id: UUID,
    data: SendMessageRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[SendMessage, Depends(get_send_message_use_case)],
) -> SendMessageResponse:
    started_at = perf_counter()
    try:
        response = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            message=data.message,
            limit=data.limit,
            offset=data.offset,
            conversation_id=data.conversation_id,
            start_new_conversation=data.start_new_conversation,
            retrieval_strategy=data.retrieval_strategy,
            retrieval_filters=(
                data.retrieval_filters.model_dump(exclude_none=True)
                if data.retrieval_filters is not None
                else None
            ),
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        ) from None
    except LLMGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None

    elapsed_ms = (perf_counter() - started_at) * 1000.0
    logger.info(
        "chat_message",
        extra={
            "project_id": str(project_id),
            "user_id": str(user_id),
            "limit": data.limit,
            "chunks_count": len(response.chunks),
            "llm_backend": settings.llm_backend,
            "elapsed_ms": round(elapsed_ms, 2),
        },
    )
    return SendMessageResponse(
        project_id=response.project_id,
        conversation_id=response.conversation_id,
        message=response.message,
        answer=response.answer,
        retrieval_strategy_used=response.retrieval_strategy_used,
        retrieval_execution_time_ms=response.retrieval_execution_time_ms,
        history_messages_used=response.history_messages_used,
        chunks_used=response.chunks_used,
        chunks=[
            RetrievedChunkResponse(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                document_file_name=chunk.document_file_name,
                content=chunk.content,
                score=chunk.score,
                vector_score=chunk.vector_score,
                fulltext_score=chunk.fulltext_score,
            )
            for chunk in response.chunks
        ],
    )


@router.post("/messages/stream")
async def stream_message(
    project_id: UUID,
    data: SendMessageRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[SendMessage, Depends(get_send_message_use_case)],
) -> StreamingResponse:
    from raggae.application.dto.chat_stream_event import ChatStreamDone, ChatStreamToken

    async def event_stream() -> AsyncIterator[str]:
        started_at = perf_counter()
        try:
            stream = use_case.execute_stream(
                project_id=project_id,
                user_id=user_id,
                message=data.message,
                limit=data.limit,
                offset=data.offset,
                conversation_id=data.conversation_id,
                start_new_conversation=data.start_new_conversation,
                retrieval_strategy=data.retrieval_strategy,
                retrieval_filters=(
                    data.retrieval_filters.model_dump(exclude_none=True)
                    if data.retrieval_filters is not None
                    else None
                ),
            )
            async for event in stream:
                if isinstance(event, ChatStreamToken):
                    yield f"data: {json.dumps({'token': event.token})}\n\n"
                elif isinstance(event, ChatStreamDone):
                    chunks_payload = [
                        {
                            "chunk_id": str(chunk.chunk_id),
                            "document_id": str(chunk.document_id),
                            "document_file_name": chunk.document_file_name,
                            "content": chunk.content,
                            "score": chunk.score,
                            "vector_score": chunk.vector_score,
                            "fulltext_score": chunk.fulltext_score,
                        }
                        for chunk in event.chunks
                    ]
                    yield (
                        "data: "
                        + json.dumps(
                            {
                                "done": True,
                                "conversation_id": str(event.conversation_id),
                                "retrieval_strategy_used": event.retrieval_strategy_used,
                                "retrieval_execution_time_ms": event.retrieval_execution_time_ms,
                                "history_messages_used": event.history_messages_used,
                                "chunks_used": event.chunks_used,
                                "chunks": chunks_payload,
                            }
                        )
                        + "\n\n"
                    )
                    elapsed_ms = (perf_counter() - started_at) * 1000.0
                    logger.info(
                        "chat_message_stream",
                        extra={
                            "project_id": str(project_id),
                            "user_id": str(user_id),
                            "limit": data.limit,
                            "chunks_count": len(event.chunks),
                            "llm_backend": settings.llm_backend,
                            "elapsed_ms": round(elapsed_ms, 2),
                        },
                    )
        except ProjectNotFoundError:
            yield f"data: {json.dumps({'error': 'Project not found'})}\n\n"
        except ConversationNotFoundError:
            yield f"data: {json.dumps({'error': 'Conversation not found'})}\n\n"
        except LLMGenerationError as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/conversations/{conversation_id}/messages")
async def list_conversation_messages(
    project_id: UUID,
    conversation_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListConversationMessages, Depends(get_list_conversation_messages_use_case)],
    limit: int = 50,
    offset: int = 0,
) -> list[MessageResponse]:
    try:
        messages = await use_case.execute(
            project_id=project_id,
            conversation_id=conversation_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        ) from None

    return [
        MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            source_documents=message.source_documents,
            reliability_percent=message.reliability_percent,
            created_at=message.created_at,
        )
        for message in messages
    ]


@router.get("/conversations")
async def list_conversations(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListConversations, Depends(get_list_conversations_use_case)],
    limit: int = 50,
    offset: int = 0,
) -> list[ConversationResponse]:
    try:
        conversations = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None

    return [
        ConversationResponse(
            id=conversation.id,
            project_id=conversation.project_id,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            title=conversation.title,
        )
        for conversation in conversations
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    project_id: UUID,
    conversation_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[GetConversation, Depends(get_get_conversation_use_case)],
) -> ConversationDetailResponse:
    try:
        conversation = await use_case.execute(
            project_id=project_id,
            conversation_id=conversation_id,
            user_id=user_id,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        ) from None

    return ConversationDetailResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        user_id=conversation.user_id,
        created_at=conversation.created_at,
        title=conversation.title,
        message_count=conversation.message_count,
        last_message=(
            MessageResponse(
                id=conversation.last_message.id,
                conversation_id=conversation.last_message.conversation_id,
                role=conversation.last_message.role,
                content=conversation.last_message.content,
                created_at=conversation.last_message.created_at,
            )
            if conversation.last_message is not None
            else None
        ),
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    project_id: UUID,
    conversation_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeleteConversation, Depends(get_delete_conversation_use_case)],
) -> None:
    try:
        await use_case.execute(
            project_id=project_id,
            conversation_id=conversation_id,
            user_id=user_id,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        ) from None


@router.patch("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_conversation(
    project_id: UUID,
    conversation_id: UUID,
    data: UpdateConversationRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateConversation, Depends(get_update_conversation_use_case)],
) -> None:
    try:
        await use_case.execute(
            project_id=project_id,
            conversation_id=conversation_id,
            user_id=user_id,
            title=data.title,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        ) from None
