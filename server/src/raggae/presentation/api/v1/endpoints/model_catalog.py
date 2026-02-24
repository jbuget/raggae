from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from raggae.presentation.api.dependencies import get_current_user_id
from raggae.presentation.api.v1.schemas.model_catalog_schemas import (
    ModelCatalogResponse,
    ModelEntry,
)

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
                ModelEntry(id="text-embedding-3-large", label="Text Embedding 3 Large"),
                ModelEntry(id="text-embedding-3-small", label="Text Embedding 3 Small"),
                ModelEntry(id="text-embedding-ada-002", label="Text Embedding Ada 002 (legacy)"),
            ],
            "gemini": [
                ModelEntry(id="gemini-embedding-001", label="Gemini Embedding 001"),
                ModelEntry(
                    id="text-multilingual-embedding-002",
                    label="Text Multilingual Embedding 002 (legacy)",
                ),
            ],
            "ollama": [
                ModelEntry(id="nomic-embed-text", label="Nomic Embed Text"),
                ModelEntry(id="mxbai-embed-large", label="MXBai Embed Large"),
                ModelEntry(id="all-minilm", label="All MiniLM"),
            ],
            "inmemory": [
                ModelEntry(id="inmemory-embed-accurate", label="InMemory Accurate"),
                ModelEntry(id="inmemory-embed-balanced", label="InMemory Balanced"),
                ModelEntry(id="inmemory-embed-fast", label="InMemory Fast"),
            ],
        },
        llm={
            "openai": [
                ModelEntry(id="gpt-5.2", label="GPT-5.2"),
                ModelEntry(id="gpt-5.2-pro", label="GPT-5.2 Pro"),
                ModelEntry(id="gpt-5.1", label="GPT-5.1"),
                ModelEntry(id="gpt-5", label="GPT-5"),
                ModelEntry(id="gpt-5-mini", label="GPT-5 Mini"),
                ModelEntry(id="gpt-5-nano", label="GPT-5 Nano"),
                ModelEntry(id="gpt-4.1", label="GPT-4.1 (legacy)"),
                ModelEntry(id="gpt-4.1-mini", label="GPT-4.1 Mini (legacy)"),
                ModelEntry(id="gpt-4.1-nano", label="GPT-4.1 Nano (legacy)"),
            ],
            "gemini": [
                ModelEntry(id="gemini-3-pro", label="Gemini 3 Pro"),
                ModelEntry(id="gemini-3-flash-preview", label="Gemini 3 Flash (preview)"),
                ModelEntry(id="gemini-3.1-pro-preview", label="Gemini 3.1 Pro (preview)"),
                ModelEntry(id="gemini-2.5-pro", label="Gemini 2.5 Pro"),
                ModelEntry(id="gemini-2.5-flash", label="Gemini 2.5 Flash"),
                ModelEntry(id="gemini-2.5-flash-lite", label="Gemini 2.5 Flash Lite"),
                ModelEntry(id="gemini-2.0-flash", label="Gemini 2.0 Flash (legacy)"),
                ModelEntry(id="gemini-2.0-flash-lite", label="Gemini 2.0 Flash Lite (legacy)"),
            ],
            "anthropic": [
                ModelEntry(id="claude-opus-4-6-20260205", label="Claude Opus 4.6"),
                ModelEntry(id="claude-opus-4-5-20251101", label="Claude Opus 4.5 (legacy)"),
                ModelEntry(id="claude-sonnet-4-6-20260217", label="Claude Sonnet 4.6"),
                ModelEntry(id="claude-sonnet-4-20250514", label="Claude Sonnet 4 (legacy)"),
                ModelEntry(id="claude-haiku-4-5-20251001", label="Claude Haiku 4.5"),
            ],
            "ollama": [
                ModelEntry(id="llama3.1:8b", label="Llama 3.1 8B"),
                ModelEntry(id="mistral:7b", label="Mistral 7B"),
                ModelEntry(id="qwen2.5:7b", label="Qwen 2.5 7B"),
            ],
            "inmemory": [
                ModelEntry(id="inmemory-chat-accurate", label="InMemory Accurate"),
                ModelEntry(id="inmemory-chat-balanced", label="InMemory Balanced"),
                ModelEntry(id="inmemory-chat-fast", label="InMemory Fast"),
            ],
        },
    )
