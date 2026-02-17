from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from raggae.presentation.api.dependencies import get_current_user_id
from raggae.presentation.api.v1.schemas.model_catalog_schemas import ModelCatalogResponse

router = APIRouter(
    prefix="/model-catalog",
    tags=["model-catalog"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get("")
async def get_model_catalog(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> ModelCatalogResponse:
    del user_id
    return ModelCatalogResponse(
        embedding={
            "openai": [
                "text-embedding-3-large",
                "text-embedding-3-small",
                "text-embedding-ada-002",
            ],
            "gemini": [
                "text-embedding-004",
                "gemini-embedding-001",
                "text-multilingual-embedding-002",
            ],
            "ollama": ["nomic-embed-text", "mxbai-embed-large", "all-minilm"],
            "inmemory": [
                "inmemory-embed-accurate",
                "inmemory-embed-balanced",
                "inmemory-embed-fast",
            ],
        },
        llm={
            "openai": ["gpt-4.1", "gpt-4.1-mini", "gpt-4o-mini"],
            "gemini": ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-pro"],
            "anthropic": [
                "claude-3-7-sonnet-latest",
                "claude-3-5-sonnet-latest",
                "claude-3-5-haiku-latest",
            ],
            "ollama": ["llama3.1:8b", "mistral:7b", "qwen2.5:7b"],
            "inmemory": [
                "inmemory-chat-accurate",
                "inmemory-chat-balanced",
                "inmemory-chat-fast",
            ],
        },
    )
