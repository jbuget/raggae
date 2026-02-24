from raggae.domain.exceptions.conversation_exceptions import ConversationNotFoundError
from raggae.domain.exceptions.document_exceptions import (
    DocumentExtractionError,
    DocumentNotFoundError,
    DocumentTooLargeError,
    EmbeddingGenerationError,
    InvalidDocumentTypeError,
    LLMGenerationError,
)
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    InvalidProjectRetrievalMinScoreError,
    InvalidProjectRetrievalStrategyError,
    InvalidProjectRetrievalTopKError,
    ProjectAlreadyPublishedError,
    ProjectAPIKeyNotOwnedError,
    ProjectNotFoundError,
)
from raggae.domain.exceptions.provider_credential_exceptions import (
    DuplicateProviderCredentialError,
    ProviderCredentialNotFoundError,
)
from raggae.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserAlreadyInactiveError,
)
from raggae.domain.exceptions.validation_errors import (
    InvalidEmailError,
    InvalidModelProviderError,
    InvalidProviderApiKeyError,
    WeakPasswordError,
)

__all__ = [
    "DocumentNotFoundError",
    "DocumentTooLargeError",
    "ConversationNotFoundError",
    "DocumentExtractionError",
    "EmbeddingGenerationError",
    "LLMGenerationError",
    "DuplicateProviderCredentialError",
    "ProviderCredentialNotFoundError",
    "InvalidCredentialsError",
    "InvalidDocumentTypeError",
    "InvalidEmailError",
    "InvalidModelProviderError",
    "InvalidProviderApiKeyError",
    "InvalidProjectEmbeddingBackendError",
    "InvalidProjectLLMBackendError",
    "InvalidProjectRetrievalMinScoreError",
    "InvalidProjectRetrievalTopKError",
    "InvalidProjectRetrievalStrategyError",
    "ProjectAPIKeyNotOwnedError",
    "ProjectAlreadyPublishedError",
    "ProjectNotFoundError",
    "UserAlreadyExistsError",
    "UserAlreadyInactiveError",
    "WeakPasswordError",
]
