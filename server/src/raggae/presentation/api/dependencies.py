from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from raggae.application.interfaces.repositories.conversation_repository import (
    ConversationRepository,
)
from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.document_repository import (
    DocumentRepository,
)
from raggae.application.interfaces.repositories.message_repository import MessageRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.application.interfaces.services.chunk_retrieval_service import (
    ChunkRetrievalService,
)
from raggae.application.interfaces.services.conversation_title_generator import (
    ConversationTitleGenerator,
)
from raggae.application.interfaces.services.document_structure_analyzer import (
    DocumentStructureAnalyzer,
)
from raggae.application.interfaces.services.document_text_extractor import (
    DocumentTextExtractor,
)
from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.application.interfaces.services.file_storage_service import FileStorageService
from raggae.application.interfaces.services.llm_service import LLMService
from raggae.application.interfaces.services.text_chunker_service import TextChunkerService
from raggae.application.interfaces.services.text_sanitizer_service import (
    TextSanitizerService,
)
from raggae.application.services.chunking_strategy_selector import (
    DeterministicChunkingStrategySelector,
)
from raggae.application.use_cases.chat.delete_conversation import DeleteConversation
from raggae.application.use_cases.chat.get_conversation import GetConversation
from raggae.application.use_cases.chat.list_conversation_messages import (
    ListConversationMessages,
)
from raggae.application.use_cases.chat.list_conversations import ListConversations
from raggae.application.use_cases.chat.query_relevant_chunks import QueryRelevantChunks
from raggae.application.use_cases.chat.send_message import SendMessage
from raggae.application.use_cases.chat.update_conversation import UpdateConversation
from raggae.application.use_cases.document.delete_document import DeleteDocument
from raggae.application.use_cases.document.get_document_file import GetDocumentFile
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
from raggae.infrastructure.database.repositories.in_memory_conversation_repository import (
    InMemoryConversationRepository,
)
from raggae.infrastructure.database.repositories.in_memory_document_chunk_repository import (
    InMemoryDocumentChunkRepository,
)
from raggae.infrastructure.database.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)
from raggae.infrastructure.database.repositories.in_memory_message_repository import (
    InMemoryMessageRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.database.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_conversation_repository import (
    SQLAlchemyConversationRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_document_chunk_repository import (
    SQLAlchemyDocumentChunkRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_document_repository import (
    SQLAlchemyDocumentRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_message_repository import (
    SQLAlchemyMessageRepository,
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
from raggae.infrastructure.services.gemini_llm_service import GeminiLLMService
from raggae.infrastructure.services.heading_section_text_chunker_service import (
    HeadingSectionTextChunkerService,
)
from raggae.infrastructure.services.heuristic_document_structure_analyzer import (
    HeuristicDocumentStructureAnalyzer,
)
from raggae.infrastructure.services.in_memory_chunk_retrieval_service import (
    InMemoryChunkRetrievalService,
)
from raggae.infrastructure.services.in_memory_embedding_service import (
    InMemoryEmbeddingService,
)
from raggae.infrastructure.services.in_memory_file_storage_service import (
    InMemoryFileStorageService,
)
from raggae.infrastructure.services.in_memory_llm_service import InMemoryLLMService
from raggae.infrastructure.services.jwt_token_service import JwtTokenService
from raggae.infrastructure.services.llamaindex_text_chunker_service import (
    LlamaIndexTextChunkerService,
)
from raggae.infrastructure.services.llm_conversation_title_generator import (
    LLMConversationTitleGenerator,
)
from raggae.infrastructure.services.minio_file_storage_service import (
    MinioFileStorageService,
)
from raggae.infrastructure.services.multiformat_document_text_extractor import (
    MultiFormatDocumentTextExtractor,
)
from raggae.infrastructure.services.ollama_llm_service import OllamaLLMService
from raggae.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService
from raggae.infrastructure.services.openai_llm_service import OpenAILLMService
from raggae.infrastructure.services.paragraph_text_chunker_service import (
    ParagraphTextChunkerService,
)
from raggae.infrastructure.services.simple_text_chunker_service import (
    SimpleTextChunkerService,
)
from raggae.infrastructure.services.simple_text_sanitizer_service import (
    SimpleTextSanitizerService,
)
from raggae.infrastructure.services.sqlalchemy_chunk_retrieval_service import (
    SQLAlchemyChunkRetrievalService,
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
    _conversation_repository: ConversationRepository = SQLAlchemyConversationRepository(
        session_factory=SessionFactory
    )
    _message_repository: MessageRepository = SQLAlchemyMessageRepository(
        session_factory=SessionFactory
    )
    _chunk_retrieval_service: ChunkRetrievalService = SQLAlchemyChunkRetrievalService(
        session_factory=SessionFactory,
        vector_weight=settings.retrieval_vector_weight,
        fulltext_weight=settings.retrieval_fulltext_weight,
        candidate_multiplier=settings.retrieval_candidate_multiplier,
    )
else:
    _user_repository = InMemoryUserRepository()
    _project_repository = InMemoryProjectRepository()
    _document_repository = InMemoryDocumentRepository()
    _document_chunk_repository = InMemoryDocumentChunkRepository()
    _conversation_repository = InMemoryConversationRepository()
    _message_repository = InMemoryMessageRepository()
    _chunk_retrieval_service = InMemoryChunkRetrievalService(
        document_repository=_document_repository,
        document_chunk_repository=_document_chunk_repository,
        vector_weight=settings.retrieval_vector_weight,
        fulltext_weight=settings.retrieval_fulltext_weight,
    )
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
if settings.text_chunker_backend == "llamaindex":
    _text_chunker_service: TextChunkerService = LlamaIndexTextChunkerService(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
elif settings.text_chunker_backend == "native":
    _fixed_window_chunker: TextChunkerService = SimpleTextChunkerService(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    _paragraph_chunker = ParagraphTextChunkerService(chunk_size=settings.chunk_size)
    _heading_section_chunker = HeadingSectionTextChunkerService(
        fallback_chunker=_fixed_window_chunker
    )
    _text_chunker_service = AdaptiveTextChunkerService(
        fixed_window_chunker=_fixed_window_chunker,
        paragraph_chunker=_paragraph_chunker,
        heading_section_chunker=_heading_section_chunker,
        context_window_size=settings.chunk_overlap,
    )
else:
    raise ValueError(f"Unsupported text chunker backend: {settings.text_chunker_backend}")
_token_service = JwtTokenService(secret_key="dev-secret-key", algorithm="HS256")
_bearer = HTTPBearer(auto_error=False)
if settings.llm_backend == "openai":
    _llm_service: LLMService = OpenAILLMService(
        api_key=settings.openai_api_key,
        model=settings.openai_llm_model,
    )
elif settings.llm_backend == "gemini":
    _llm_service = GeminiLLMService(
        api_key=settings.gemini_api_key,
        model=settings.gemini_llm_model,
    )
elif settings.llm_backend == "ollama":
    _llm_service = OllamaLLMService(
        base_url=settings.ollama_base_url,
        model=settings.ollama_llm_model,
        timeout_seconds=settings.llm_request_timeout_seconds,
        keep_alive=settings.ollama_keep_alive,
    )
else:
    _llm_service = InMemoryLLMService()
_conversation_title_generator: ConversationTitleGenerator = LLMConversationTitleGenerator(
    llm_service=_llm_service
)


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
        chunker_backend=settings.text_chunker_backend,
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


def get_get_document_file_use_case() -> GetDocumentFile:
    return GetDocumentFile(
        document_repository=_document_repository,
        project_repository=_project_repository,
        file_storage_service=_file_storage_service,
    )


def get_query_relevant_chunks_use_case() -> QueryRelevantChunks:
    return QueryRelevantChunks(
        project_repository=_project_repository,
        embedding_service=_embedding_service,
        chunk_retrieval_service=_chunk_retrieval_service,
        min_score=settings.retrieval_min_score,
    )


def get_send_message_use_case() -> SendMessage:
    return SendMessage(
        query_relevant_chunks_use_case=get_query_relevant_chunks_use_case(),
        llm_service=_llm_service,
        conversation_title_generator=_conversation_title_generator,
        project_repository=_project_repository,
        conversation_repository=_conversation_repository,
        message_repository=_message_repository,
    )


def get_list_conversation_messages_use_case() -> ListConversationMessages:
    return ListConversationMessages(
        project_repository=_project_repository,
        conversation_repository=_conversation_repository,
        message_repository=_message_repository,
    )


def get_list_conversations_use_case() -> ListConversations:
    return ListConversations(
        project_repository=_project_repository,
        conversation_repository=_conversation_repository,
    )


def get_delete_conversation_use_case() -> DeleteConversation:
    return DeleteConversation(
        project_repository=_project_repository,
        conversation_repository=_conversation_repository,
    )


def get_get_conversation_use_case() -> GetConversation:
    return GetConversation(
        project_repository=_project_repository,
        conversation_repository=_conversation_repository,
        message_repository=_message_repository,
    )


def get_update_conversation_use_case() -> UpdateConversation:
    return UpdateConversation(
        project_repository=_project_repository,
        conversation_repository=_conversation_repository,
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
