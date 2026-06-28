from uuid import UUID

from raggae.application.dto.document_dto import DocumentDTO
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.application.interfaces.services.project_embedding_service_resolver import (
    ProjectEmbeddingServiceResolver,
)
from raggae.application.services.agent_configuration_resolver import (
    AgentConfigurationResolver,
)
from raggae.application.services.document_indexing_service import DocumentIndexingService
from raggae.domain.entities import Project
from raggae.domain.exceptions.document_exceptions import (
    DocumentExtractionError,
    DocumentNotFoundError,
    EmbeddingGenerationError,
)
from raggae.domain.exceptions.project_exceptions import (
    ProjectNotFoundError,
    ProjectReindexInProgressError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.document_status import DocumentStatus
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.domain.value_objects.resolved_agent_configuration import ResolvedAgentConfiguration
from raggae.infrastructure.config.settings import settings


class ReindexDocument:
    """Use Case: Re-run the indexing pipeline on an existing document."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        project_repository: ProjectRepository,
        file_storage_service: FileStorageService,
        document_indexing_service: DocumentIndexingService,
        project_embedding_service_resolver: ProjectEmbeddingServiceResolver | None = None,
        organization_member_repository: OrganizationMemberRepository | None = None,
        agent_configuration_resolver: AgentConfigurationResolver | None = None,
    ) -> None:
        self._document_repository = document_repository
        self._project_repository = project_repository
        self._file_storage_service = file_storage_service
        self._document_indexing_service = document_indexing_service
        self._project_embedding_service_resolver = project_embedding_service_resolver
        self._organization_member_repository = organization_member_repository
        self._agent_configuration_resolver = agent_configuration_resolver

    async def execute(
        self,
        project_id: UUID,
        document_id: UUID,
        user_id: UUID,
    ) -> DocumentDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        if project.user_id != user_id:
            if project.organization_id is None or self._organization_member_repository is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
            member = await self._organization_member_repository.find_by_organization_and_user(
                organization_id=project.organization_id,
                user_id=user_id,
            )
            if member is None or member.role not in {
                OrganizationMemberRole.OWNER,
                OrganizationMemberRole.MAKER,
            }:
                raise ProjectNotFoundError(f"Project {project_id} not found")
        if project.is_reindexing():
            raise ProjectReindexInProgressError(f"Project {project_id} is currently reindexing")

        document = await self._document_repository.find_by_id(document_id)
        if document is None or document.project_id != project_id:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        resolved = await self._resolve_config(project, user_id)
        parent_child_chunking = (
            resolved.parent_child_chunking
            if resolved and resolved.parent_child_chunking is not None
            else settings.default_parent_child_chunking
        )
        chunking_strategy = None
        if resolved and resolved.chunking_strategy:
            try:
                chunking_strategy = ChunkingStrategy(resolved.chunking_strategy)
            except ValueError:
                pass

        try:
            if document.status != DocumentStatus.PROCESSING:
                document = document.transition_to(DocumentStatus.PROCESSING)
                await self._document_repository.save(document)

            file_content, _ = await self._file_storage_service.download_file(document.storage_key)

            embedding_service = None
            if self._project_embedding_service_resolver is not None:
                encrypted_api_key = (
                    await self._resolve_embedding_api_key(resolved, project, user_id) if resolved else None
                )
                embedding_service = self._project_embedding_service_resolver.resolve(
                    backend=resolved.embedding_backend if resolved else None,
                    model=resolved.embedding_model if resolved else None,
                    encrypted_api_key=encrypted_api_key,
                )

            document = await self._document_indexing_service.run_pipeline(
                document=document,
                project=project,
                file_content=file_content,
                embedding_service=embedding_service,
                parent_child_chunking=parent_child_chunking,
                chunking_strategy=chunking_strategy,
            )
            document = document.transition_to(DocumentStatus.INDEXED)
        except (DocumentExtractionError, EmbeddingGenerationError, FileNotFoundError) as exc:
            document = document.transition_to(DocumentStatus.ERROR, error_message=str(exc))

        await self._document_repository.save(document)
        return DocumentDTO.from_entity(document)

    async def _resolve_config(self, project: Project, user_id: UUID) -> ResolvedAgentConfiguration | None:
        if self._agent_configuration_resolver is None:
            return None
        return await self._agent_configuration_resolver.resolve(project=project, user_id=user_id)

    async def _resolve_embedding_api_key(
        self, resolved: ResolvedAgentConfiguration, project: Project, user_id: UUID
    ) -> str | None:
        if self._agent_configuration_resolver is None:
            return None
        return await self._agent_configuration_resolver.fetch_encrypted_api_key(
            credential_id=resolved.embedding_api_key_credential_id,
            project=project,
            user_id=user_id,
        )
