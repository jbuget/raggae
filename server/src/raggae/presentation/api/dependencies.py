from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.document_repository import (
    DocumentRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.application.interfaces.services.document_structure_analyzer import (
    DocumentStructureAnalyzer,
)
from raggae.application.interfaces.services.document_text_extractor import (
    DocumentTextExtractor,
)
from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.application.interfaces.services.text_chunker_service import TextChunkerService
from raggae.application.interfaces.services.text_sanitizer_service import (
    TextSanitizerService,
)
from raggae.application.services.chunking_strategy_selector import (
    DeterministicChunkingStrategySelector,
)
from raggae.application.use_cases.document.delete_document import DeleteDocument
from raggae.application.use_cases.document.list_document_chunks import ListDocumentChunks
from raggae.application.use_cases.document.list_project_documents import ListProjectDocuments
from raggae.application.use_cases.document.upload_document import UploadDocument
from raggae.application.use_cases.project.create_project import CreateProject
from raggae.application.use_cases.project.delete_project import DeleteProject
from raggae.application.use_cases.project.get_project import GetProject
from raggae.application.use_cases.project.list_projects import ListProjects
from raggae.application.use_cases.project.update_project import UpdateProject
from raggae.application.use_cases.user.login_user import LoginUser
from raggae.application.use_cases.user.register_user import RegisterUser
from raggae.infrastructure.config.settings import settings
from raggae.infrastructure.database.repositories.in_memory_document_chunk_repository import (
    InMemoryDocumentChunkRepository,
)
from raggae.infrastructure.database.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.database.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_document_chunk_repository import (
    SQLAlchemyDocumentChunkRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_document_repository import (
    SQLAlchemyDocumentRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from raggae.infrastructure.database.session import SessionFactory
from raggae.infrastructure.services.adaptive_text_chunker_service import (
    AdaptiveTextChunkerService,
)
from raggae.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from raggae.infrastructure.services.heading_section_text_chunker_service import (
    HeadingSectionTextChunkerService,
)
from raggae.infrastructure.services.heuristic_document_structure_analyzer import (
    HeuristicDocumentStructureAnalyzer,
)
from raggae.infrastructure.services.in_memory_embedding_service import (
    InMemoryEmbeddingService,
)
from raggae.infrastructure.services.in_memory_file_storage_service import (
    InMemoryFileStorageService,
)
from raggae.infrastructure.services.jwt_token_service import JwtTokenService
from raggae.infrastructure.services.minio_file_storage_service import (
    MinioFileStorageService,
)
from raggae.infrastructure.services.multiformat_document_text_extractor import (
    MultiFormatDocumentTextExtractor,
)
from raggae.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService
from raggae.infrastructure.services.paragraph_text_chunker_service import (
    ParagraphTextChunkerService,
)
from raggae.infrastructure.services.simple_text_chunker_service import (
    SimpleTextChunkerService,
)
from raggae.infrastructure.services.simple_text_sanitizer_service import (
    SimpleTextSanitizerService,
)

if settings.persistence_backend == "postgres":
    _user_repository: UserRepository = SQLAlchemyUserRepository(session_factory=SessionFactory)
    _project_repository: ProjectRepository = SQLAlchemyProjectRepository(
        session_factory=SessionFactory
    )
    _document_repository: DocumentRepository = SQLAlchemyDocumentRepository(
        session_factory=SessionFactory
    )
    _document_chunk_repository: DocumentChunkRepository = SQLAlchemyDocumentChunkRepository(
        session_factory=SessionFactory
    )
else:
    _user_repository = InMemoryUserRepository()
    _project_repository = InMemoryProjectRepository()
    _document_repository = InMemoryDocumentRepository()
    _document_chunk_repository = InMemoryDocumentChunkRepository()
_password_hasher = BcryptPasswordHasher()
if settings.storage_backend == "minio":
    _file_storage_service: FileStorageService = MinioFileStorageService(
        endpoint=settings.s3_endpoint_url,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        bucket_name=settings.s3_bucket_name,
        secure=settings.s3_secure,
    )
else:
    _file_storage_service = InMemoryFileStorageService()
if settings.embedding_backend == "openai":
    _embedding_service: EmbeddingService = OpenAIEmbeddingService(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
    )
else:
    _embedding_service = InMemoryEmbeddingService(dimension=settings.embedding_dimension)
_document_text_extractor: DocumentTextExtractor = MultiFormatDocumentTextExtractor()
_text_sanitizer_service: TextSanitizerService = SimpleTextSanitizerService()
_document_structure_analyzer: DocumentStructureAnalyzer = HeuristicDocumentStructureAnalyzer()
_chunking_strategy_selector = DeterministicChunkingStrategySelector()
_fixed_window_chunker = SimpleTextChunkerService(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
)
_paragraph_chunker = ParagraphTextChunkerService(chunk_size=settings.chunk_size)
_heading_section_chunker = HeadingSectionTextChunkerService(
    fallback_chunker=_fixed_window_chunker
)
_text_chunker_service: TextChunkerService = AdaptiveTextChunkerService(
    fixed_window_chunker=_fixed_window_chunker,
    paragraph_chunker=_paragraph_chunker,
    heading_section_chunker=_heading_section_chunker,
    context_window_size=settings.chunk_overlap,
)
_token_service = JwtTokenService(secret_key="dev-secret-key", algorithm="HS256")
_bearer = HTTPBearer(auto_error=False)


def get_register_user_use_case() -> RegisterUser:
    return RegisterUser(
        user_repository=_user_repository,
        password_hasher=_password_hasher,
    )


def get_login_user_use_case() -> LoginUser:
    return LoginUser(
        user_repository=_user_repository,
        password_hasher=_password_hasher,
        token_service=_token_service,
    )


def get_create_project_use_case() -> CreateProject:
    return CreateProject(project_repository=_project_repository)


def get_get_project_use_case() -> GetProject:
    return GetProject(project_repository=_project_repository)


def get_list_projects_use_case() -> ListProjects:
    return ListProjects(project_repository=_project_repository)


def get_delete_project_use_case() -> DeleteProject:
    return DeleteProject(project_repository=_project_repository)


def get_update_project_use_case() -> UpdateProject:
    return UpdateProject(project_repository=_project_repository)


def get_upload_document_use_case() -> UploadDocument:
    return UploadDocument(
        document_repository=_document_repository,
        project_repository=_project_repository,
        file_storage_service=_file_storage_service,
        max_file_size=settings.max_upload_size,
        processing_mode=settings.processing_mode,
        document_chunk_repository=_document_chunk_repository,
        document_text_extractor=_document_text_extractor,
        text_sanitizer_service=_text_sanitizer_service,
        document_structure_analyzer=_document_structure_analyzer,
        chunking_strategy_selector=_chunking_strategy_selector,
        text_chunker_service=_text_chunker_service,
        embedding_service=_embedding_service,
    )


def get_list_project_documents_use_case() -> ListProjectDocuments:
    return ListProjectDocuments(
        document_repository=_document_repository,
        project_repository=_project_repository,
    )


def get_list_document_chunks_use_case() -> ListDocumentChunks:
    return ListDocumentChunks(
        document_repository=_document_repository,
        document_chunk_repository=_document_chunk_repository,
        project_repository=_project_repository,
    )


def get_delete_document_use_case() -> DeleteDocument:
    return DeleteDocument(
        document_repository=_document_repository,
        document_chunk_repository=_document_chunk_repository,
        project_repository=_project_repository,
        file_storage_service=_file_storage_service,
    )


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> UUID:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
        )

    user_id = _token_service.verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    return user_id
