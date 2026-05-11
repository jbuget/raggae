import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.document_dto import DocumentDTO
from raggae.application.interfaces.repositories.agent_configuration_repository import (
    AgentConfigurationRepository,
)
from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.org_provider_credential_repository import (
    OrgProviderCredentialRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.provider_credential_repository import (
    ProviderCredentialRepository,
)
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.application.interfaces.services.project_embedding_service_resolver import (
    ProjectEmbeddingServiceResolver,
)
from raggae.application.services.document_indexing_service import DocumentIndexingService
from raggae.domain.entities.document import Document
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.document_exceptions import (
    DocumentExtractionError,
    DocumentTooLargeError,
    EmbeddingGenerationError,
    InvalidDocumentTypeError,
    ProjectDocumentLimitReachedError,
)
from raggae.domain.exceptions.project_exceptions import (
    ProjectNotFoundError,
    ProjectReindexInProgressError,
)
from raggae.domain.services.config_extractor import ConfigExtractor
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.document_status import DocumentStatus
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.domain.value_objects.resolved_agent_configuration import ResolvedAgentConfiguration
from raggae.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "docx", "doc", "pptx"}


@dataclass(frozen=True)
class UploadDocumentItem:
    file_name: str
    file_content: bytes
    content_type: str


@dataclass(frozen=True)
class UploadDocumentsCreatedItem:
    original_filename: str
    stored_filename: str
    document_id: UUID


@dataclass(frozen=True)
class UploadDocumentsErrorItem:
    filename: str
    code: str
    message: str


@dataclass(frozen=True)
class UploadDocumentsResult:
    total: int
    succeeded: int
    failed: int
    created: list[UploadDocumentsCreatedItem]
    errors: list[UploadDocumentsErrorItem]


class UploadDocument:
    """Use Case: Upload and attach a document to a project."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        project_repository: ProjectRepository,
        file_storage_service: FileStorageService,
        max_file_size: int,
        processing_mode: str = "off",
        document_chunk_repository: DocumentChunkRepository | None = None,
        document_indexing_service: DocumentIndexingService | None = None,
        project_embedding_service_resolver: ProjectEmbeddingServiceResolver | None = None,
        max_documents_per_project: int | None = None,
        organization_member_repository: OrganizationMemberRepository | None = None,
        agent_configuration_repository: AgentConfigurationRepository | None = None,
        org_provider_credential_repository: OrgProviderCredentialRepository | None = None,
        provider_credential_repository: ProviderCredentialRepository | None = None,
    ) -> None:
        self._document_repository = document_repository
        self._project_repository = project_repository
        self._file_storage_service = file_storage_service
        self._max_file_size = max_file_size
        self._processing_mode = processing_mode
        if self._processing_mode not in {"off", "sync", "async"}:
            raise ValueError(f"Unsupported processing mode: {self._processing_mode}")
        self._document_chunk_repository = document_chunk_repository
        self._document_indexing_service = document_indexing_service
        self._project_embedding_service_resolver = project_embedding_service_resolver
        self._max_documents_per_project = max_documents_per_project
        self._organization_member_repository = organization_member_repository
        self._agent_configuration_repository = agent_configuration_repository
        self._org_provider_credential_repository = org_provider_credential_repository
        self._provider_credential_repository = provider_credential_repository

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        file_name: str,
        file_content: bytes,
        content_type: str,
    ) -> DocumentDTO:
        project = await self._assert_project_owner(project_id=project_id, user_id=user_id)
        await self._assert_document_quota(project_id=project_id)
        return await self._execute_single(
            project_id=project_id,
            project=project,
            user_id=user_id,
            file_name=file_name,
            file_content=file_content,
            content_type=content_type,
        )

    async def execute_many(
        self,
        project_id: UUID,
        user_id: UUID,
        files: list[UploadDocumentItem],
    ) -> UploadDocumentsResult:
        project = await self._assert_project_owner(project_id=project_id, user_id=user_id)
        existing_documents = await self._document_repository.find_by_project_id(project_id)
        indexed_by_name = {
            doc.file_name.lower() for doc in existing_documents if doc.processing_strategy is not None
        }
        existing_names = {doc.file_name.lower() for doc in existing_documents}
        request_names: set[str] = set()
        created: list[UploadDocumentsCreatedItem] = []
        errors: list[UploadDocumentsErrorItem] = []

        for item in files:
            request_name = item.file_name.lower()
            if request_name in request_names:
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="DUPLICATE_IN_REQUEST",
                        message="Duplicate filename in request.",
                    )
                )
                continue
            request_names.add(request_name)
            if request_name in indexed_by_name:
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="ALREADY_INDEXED",
                        message="Document already exists and is already indexed for this project.",
                    )
                )
                continue
            stored_filename = self._resolve_unique_filename(item.file_name, existing_names)
            try:
                document_dto = await self._execute_single(
                    project_id=project_id,
                    project=project,
                    user_id=user_id,
                    file_name=stored_filename,
                    file_content=item.file_content,
                    content_type=item.content_type,
                )
            except InvalidDocumentTypeError as exc:
                logger.warning("Upload rejected [%s] %s: %s", "INVALID_FILE_TYPE", item.file_name, exc)
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="INVALID_FILE_TYPE",
                        message=str(exc),
                    )
                )
                continue
            except DocumentTooLargeError as exc:
                logger.warning("Upload rejected [%s] %s: %s", "FILE_TOO_LARGE", item.file_name, exc)
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="FILE_TOO_LARGE",
                        message="Document exceeds maximum allowed size",
                    )
                )
                continue
            except (DocumentExtractionError, EmbeddingGenerationError) as exc:
                logger.error(
                    "Upload failed [%s] %s: %s", "PROCESSING_FAILED", item.file_name, exc, exc_info=True
                )
                errors.append(
                    UploadDocumentsErrorItem(
                        filename=item.file_name,
                        code="PROCESSING_FAILED",
                        message=str(exc),
                    )
                )
                continue

            existing_names.add(stored_filename.lower())
            created.append(
                UploadDocumentsCreatedItem(
                    original_filename=item.file_name,
                    stored_filename=stored_filename,
                    document_id=document_dto.id,
                )
            )

        return UploadDocumentsResult(
            total=len(files),
            succeeded=len(created),
            failed=len(errors),
            created=created,
            errors=errors,
        )

    async def _assert_project_owner(self, project_id: UUID, user_id: UUID) -> Project:
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
        return project

    async def _assert_document_quota(self, project_id: UUID) -> None:
        if self._max_documents_per_project is None:
            return
        existing = await self._document_repository.find_by_project_id(project_id)
        if len(existing) >= self._max_documents_per_project:
            raise ProjectDocumentLimitReachedError(
                f"Project {project_id} has reached the maximum of {self._max_documents_per_project} documents"
            )

    async def _execute_single(
        self,
        project_id: UUID,
        project: Project,
        user_id: UUID,
        file_name: str,
        file_content: bytes,
        content_type: str,
    ) -> DocumentDTO:
        extension = file_name.rsplit(".", maxsplit=1)[-1].lower() if "." in file_name else ""
        if extension not in ALLOWED_EXTENSIONS:
            raise InvalidDocumentTypeError(f"Unsupported document type: {extension}")

        file_size = len(file_content)
        if file_size > self._max_file_size:
            raise DocumentTooLargeError("Document exceeds maximum allowed size")

        document_id = uuid4()
        storage_key = f"projects/{project_id}/documents/{document_id}-{file_name}"
        await self._file_storage_service.upload_file(storage_key, file_content, content_type)

        document = Document(
            id=document_id,
            project_id=project_id,
            file_name=file_name,
            content_type=content_type,
            file_size=file_size,
            storage_key=storage_key,
            created_at=datetime.now(UTC),
            status=DocumentStatus.UPLOADED,
        )
        await self._document_repository.save(document)
        try:
            if self._processing_mode == "sync" and self._document_indexing_service is not None:
                document = document.transition_to(DocumentStatus.PROCESSING)
                await self._document_repository.save(document)
                encrypted_api_key = await self._resolve_embedding_api_key(project, user_id)
                embedding_service = (
                    self._project_embedding_service_resolver.resolve(
                        backend=await self._resolve_embedding_backend(project, user_id),
                        model=await self._resolve_embedding_model(project, user_id),
                        encrypted_api_key=encrypted_api_key,
                    )
                    if self._project_embedding_service_resolver is not None
                    else None
                )
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
                        logger.warning(f"Invalid chunking strategy in config: {resolved.chunking_strategy}")

                document = await self._document_indexing_service.run_pipeline(
                    document=document,
                    project=project,
                    file_content=file_content,
                    embedding_service=embedding_service,
                    parent_child_chunking=parent_child_chunking,
                    chunking_strategy=chunking_strategy,
                )
                document = document.transition_to(DocumentStatus.INDEXED)
                await self._document_repository.save(document)
        except (DocumentExtractionError, EmbeddingGenerationError) as exc:
            document = document.transition_to(DocumentStatus.ERROR, error_message=str(exc))
            await self._document_repository.save(document)
            await self._cleanup_failed_document(document_id=document.id, storage_key=document.storage_key)
            raise

        return DocumentDTO.from_entity(document)

    async def _resolve_embedding_backend(self, project: Project, user_id: UUID) -> str | None:
        resolved = await self._resolve_config(project, user_id)
        return resolved.embedding_backend if resolved else None

    async def _resolve_embedding_model(self, project: Project, user_id: UUID) -> str | None:
        resolved = await self._resolve_config(project, user_id)
        return resolved.embedding_model if resolved else None

    async def _resolve_embedding_api_key(self, project: Project, user_id: UUID) -> str | None:
        resolved = await self._resolve_config(project, user_id)
        if resolved is None or resolved.embedding_api_key_credential_id is None:
            return None
        return await self._fetch_encrypted_key(
            credential_id=resolved.embedding_api_key_credential_id,
            project=project,
            user_id=user_id,
        )

    async def _resolve_config(self, project: Project, user_id: UUID) -> ResolvedAgentConfiguration | None:
        if self._agent_configuration_repository is None:
            return None
        project_config = await self._agent_configuration_repository.find_by_owner(
            project.id, AgentConfigurationType.PROJECT
        )
        
        # If project_config is None, we still want to resolve from parent/app
        from uuid import uuid4
        base_config = project_config or AgentConfiguration(
            id=uuid4(), owner_id=project.id, owner_type=AgentConfigurationType.PROJECT
        )

        if project.organization_id is not None:
            parent_config = await self._agent_configuration_repository.find_by_owner(
                project.organization_id, AgentConfigurationType.ORGA
            )
        else:
            parent_config = await self._agent_configuration_repository.find_by_owner(
                user_id, AgentConfigurationType.USER
            )

        app_config = await self._agent_configuration_repository.find_app_defaults()
        return ConfigExtractor.resolve(base_config, parent_config, app_config)

    async def _fetch_encrypted_key(self, credential_id: UUID, project: Project, user_id: UUID) -> str | None:
        if project.organization_id is not None and self._org_provider_credential_repository is not None:
            org_creds = await self._org_provider_credential_repository.list_by_org_id(project.organization_id)
            org_cred = next((c for c in org_creds if c.id == credential_id), None)
            if org_cred is not None:
                return org_cred.encrypted_api_key
        if self._provider_credential_repository is not None:
            user_creds = await self._provider_credential_repository.list_by_user_id(user_id)
            user_cred = next((c for c in user_creds if c.id == credential_id), None)
            if user_cred is not None:
                return user_cred.encrypted_api_key
        return None

    async def _cleanup_failed_document(self, document_id: UUID, storage_key: str) -> None:
        await self._file_storage_service.delete_file(storage_key)
        if self._document_chunk_repository is not None:
            await self._document_chunk_repository.delete_by_document_id(document_id)
        await self._document_repository.delete(document_id)

    def _resolve_unique_filename(self, file_name: str, existing_names: set[str]) -> str:
        normalized = file_name.lower()
        if normalized not in existing_names:
            return file_name

        name, extension = file_name.rsplit(".", maxsplit=1) if "." in file_name else (file_name, "")
        index = 1
        while True:
            if extension:
                candidate = f"{name}-copie-{index}.{extension}"
            else:
                candidate = f"{name}-copie-{index}"
            if candidate.lower() not in existing_names:
                return candidate
            index += 1
