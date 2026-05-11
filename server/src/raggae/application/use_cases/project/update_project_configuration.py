from uuid import UUID, uuid4

from raggae.application.constants import (
    SUPPORTED_CHUNKING_STRATEGIES,
    SUPPORTED_EMBEDDING_BACKENDS,
    SUPPORTED_LLM_BACKENDS,
    SUPPORTED_RERANKER_BACKENDS,
    SUPPORTED_RETRIEVAL_STRATEGIES,
)
from raggae.application.dto.agent_configuration_dto import AgentConfigurationDTO
from raggae.application.interfaces.repositories.agent_configuration_repository import (
    AgentConfigurationRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.project_snapshot_repository import (
    ProjectSnapshotRepository,
)
from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    InvalidProjectRerankerBackendError,
    InvalidProjectRetrievalStrategyError,
    ProjectNotFoundError,
)
from raggae.domain.services.config_extractor import ConfigExtractor
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType


class UpdateProjectConfiguration:
    """Use Case: Update the agent configuration for a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        agent_configuration_repository: AgentConfigurationRepository,
        snapshot_repository: ProjectSnapshotRepository | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._agent_configuration_repository = agent_configuration_repository
        self._snapshot_repository = snapshot_repository

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        embedding_backend: str | None = None,
        embedding_model: str | None = None,
        embedding_api_key_credential_id: UUID | None = None,
        llm_backend: str | None = None,
        llm_model: str | None = None,
        llm_api_key_credential_id: UUID | None = None,
        chunking_strategy: str | None = None,
        parent_child_chunking: bool | None = None,
        retrieval_strategy: str | None = None,
        retrieval_top_k: int | None = None,
        retrieval_min_score: float | None = None,
        reranking_enabled: bool | None = None,
        reranker_backend: str | None = None,
        reranker_model: str | None = None,
        reranker_candidate_multiplier: int | None = None,
        chat_history_window_size: int | None = None,
        chat_history_max_chars: int | None = None,
    ) -> AgentConfigurationDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        if embedding_backend is not None and embedding_backend not in SUPPORTED_EMBEDDING_BACKENDS:
            raise InvalidProjectEmbeddingBackendError(f"Unsupported embedding backend: {embedding_backend}")
        if llm_backend is not None and llm_backend not in SUPPORTED_LLM_BACKENDS:
            raise InvalidProjectLLMBackendError(f"Unsupported LLM backend: {llm_backend}")
        if chunking_strategy is not None and chunking_strategy not in SUPPORTED_CHUNKING_STRATEGIES:
            raise ValueError(f"Unsupported chunking strategy: {chunking_strategy}")
        if retrieval_strategy is not None and retrieval_strategy not in SUPPORTED_RETRIEVAL_STRATEGIES:
            raise InvalidProjectRetrievalStrategyError(
                f"Unsupported retrieval strategy: {retrieval_strategy}"
            )
        if reranker_backend is not None and reranker_backend not in SUPPORTED_RERANKER_BACKENDS:
            raise InvalidProjectRerankerBackendError(f"Unsupported reranker backend: {reranker_backend}")

        existing = await self._agent_configuration_repository.find_by_owner(
            project_id, AgentConfigurationType.PROJECT
        )
        config = AgentConfiguration(
            id=existing.id if existing else uuid4(),
            owner_id=project_id,
            owner_type=AgentConfigurationType.PROJECT,
            embedding_backend=embedding_backend,
            embedding_model=embedding_model,
            embedding_api_key_credential_id=embedding_api_key_credential_id,
            llm_backend=llm_backend,
            llm_model=llm_model,
            llm_api_key_credential_id=llm_api_key_credential_id,
            chunking_strategy=chunking_strategy,
            parent_child_chunking=parent_child_chunking,
            retrieval_strategy=retrieval_strategy,
            retrieval_top_k=retrieval_top_k,
            retrieval_min_score=retrieval_min_score,
            reranking_enabled=reranking_enabled,
            reranker_backend=reranker_backend,
            reranker_model=reranker_model,
            reranker_candidate_multiplier=reranker_candidate_multiplier,
            chat_history_window_size=chat_history_window_size,
            chat_history_max_chars=chat_history_max_chars,
        )
        await self._agent_configuration_repository.save(config)

        if self._snapshot_repository is not None:
            # Capture the RESOLVED config for the history, so we know what was actually used
            parent_config = None
            if project.organization_id is not None:
                parent_config = await self._agent_configuration_repository.find_by_owner(
                    project.organization_id, AgentConfigurationType.ORGA
                )
            else:
                parent_config = await self._agent_configuration_repository.find_by_owner(
                    user_id, AgentConfigurationType.USER
                )
            app_config = await self._agent_configuration_repository.find_app_defaults()
            resolved = ConfigExtractor.resolve(config, parent_config, app_config)

            version_number = await self._snapshot_repository.get_next_version_number(project.id)
            snapshot = ProjectSnapshot.from_project(
                project=project,
                version_number=version_number,
                created_by_user_id=user_id,
                agent_config=resolved,  # Pass resolved instead of overrides
            )
            await self._snapshot_repository.save(snapshot)

        return AgentConfigurationDTO.from_entity(config)
