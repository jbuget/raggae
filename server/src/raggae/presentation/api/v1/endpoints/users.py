from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from raggae.application.use_cases.chat.list_favorite_conversations import ListFavoriteConversations
from raggae.presentation.api.dependencies import (
    get_current_user_id,
    get_list_favorite_conversations_use_case,
)
from raggae.presentation.api.v1.schemas.chat_schemas import FavoriteConversationResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get("/me/conversations/favorites")
async def list_favorite_conversations(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListFavoriteConversations, Depends(get_list_favorite_conversations_use_case)],
    limit: int = 50,
    offset: int = 0,
) -> list[FavoriteConversationResponse]:
    results = await use_case.execute(user_id=user_id, limit=limit, offset=offset)
    return [
        FavoriteConversationResponse(
            id=result.conversation.id,
            project_id=result.conversation.project_id,
            user_id=result.conversation.user_id,
            created_at=result.conversation.created_at,
            title=result.conversation.title,
            is_favorite=result.conversation.is_favorite,
            project_name=result.project_name,
        )
        for result in results
    ]
