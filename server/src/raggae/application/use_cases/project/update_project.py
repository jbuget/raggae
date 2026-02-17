from dataclasses import replace
from uuid import UUID

from raggae.application.constants import MAX_PROJECT_SYSTEM_PROMPT_LENGTH
from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    ProjectNotFoundError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy

_SUPPORTED_EMBEDDING_BACKENDS = {"openai", "gemini", "ollama", "inmemory"}
_SUPPORTED_LLM_BACKENDS = {"openai", "gemini", "anthropic", "ollama", "inmemory"}


class UpdateProject:
    """Use Case: Update a project."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(
        self,
        project_id: UUID,
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
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        if embedding_backend is not None and embedding_backend not in _SUPPORTED_EMBEDDING_BACKENDS:
            raise InvalidProjectEmbeddingBackendError(
                f"Unsupported embedding backend: {embedding_backend}"
            )
        if llm_backend is not None and llm_backend not in _SUPPORTED_LLM_BACKENDS:
            raise InvalidProjectLLMBackendError(f"Unsupported llm backend: {llm_backend}")

        updated_project = replace(
            project,
            name=name,
            description=description,
            system_prompt=system_prompt,
            chunking_strategy=project.chunking_strategy
            if chunking_strategy is None
            else chunking_strategy,
            parent_child_chunking=project.parent_child_chunking
            if parent_child_chunking is None
            else parent_child_chunking,
            embedding_backend=project.embedding_backend
            if embedding_backend is None
            else embedding_backend,
            embedding_model=project.embedding_model if embedding_model is None else embedding_model,
            embedding_api_key_encrypted=project.embedding_api_key_encrypted
            if embedding_api_key_encrypted is None
            else embedding_api_key_encrypted,
            llm_backend=project.llm_backend if llm_backend is None else llm_backend,
            llm_model=project.llm_model if llm_model is None else llm_model,
            llm_api_key_encrypted=project.llm_api_key_encrypted
            if llm_api_key_encrypted is None
            else llm_api_key_encrypted,
        )
        await self._project_repository.save(updated_project)
        return ProjectDTO.from_entity(updated_project)
