from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.constants import MAX_PROJECT_SYSTEM_PROMPT_LENGTH
from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy

_SUPPORTED_EMBEDDING_BACKENDS = {"openai", "gemini", "ollama", "inmemory"}
_SUPPORTED_LLM_BACKENDS = {"openai", "gemini", "anthropic", "ollama", "inmemory"}


class CreateProject:
    """Use Case: Create a new project."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(
        self,
        user_id: UUID,
        name: str,
        description: str,
        system_prompt: str,
        chunking_strategy: ChunkingStrategy | None = None,
        parent_child_chunking: bool | None = None,
        embedding_backend: str | None = None,
        embedding_model: str | None = None,
        embedding_api_key_encrypted: str | None = None,
        llm_backend: str | None = None,
        llm_model: str | None = None,
        llm_api_key_encrypted: str | None = None,
    ) -> ProjectDTO:
        if len(system_prompt) > MAX_PROJECT_SYSTEM_PROMPT_LENGTH:
            raise ProjectSystemPromptTooLongError(
                f"System prompt exceeds {MAX_PROJECT_SYSTEM_PROMPT_LENGTH} characters"
            )
        if embedding_backend is not None and embedding_backend not in _SUPPORTED_EMBEDDING_BACKENDS:
            raise InvalidProjectEmbeddingBackendError(
                f"Unsupported embedding backend: {embedding_backend}"
            )
        if llm_backend is not None and llm_backend not in _SUPPORTED_LLM_BACKENDS:
            raise InvalidProjectLLMBackendError(f"Unsupported llm backend: {llm_backend}")
        project = Project(
            id=uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            is_published=False,
            created_at=datetime.now(UTC),
            chunking_strategy=chunking_strategy or ChunkingStrategy.AUTO,
            parent_child_chunking=parent_child_chunking or False,
            embedding_backend=embedding_backend,
            embedding_model=embedding_model,
            embedding_api_key_encrypted=embedding_api_key_encrypted,
            llm_backend=llm_backend,
            llm_model=llm_model,
            llm_api_key_encrypted=llm_api_key_encrypted,
        )

        await self._project_repository.save(project)

        return ProjectDTO.from_entity(project)
