from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.application.interfaces.services.provider_api_key_crypto_service import (
    ProviderApiKeyCryptoService,
)
from raggae.infrastructure.config.settings import Settings
from raggae.infrastructure.services.contextual_embedding_service import (
    ContextualEmbeddingService,
)
from raggae.infrastructure.services.gemini_embedding_service import GeminiEmbeddingService
from raggae.infrastructure.services.in_memory_embedding_service import InMemoryEmbeddingService
from raggae.infrastructure.services.ollama_embedding_service import OllamaEmbeddingService
from raggae.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService


class ProjectEmbeddingServiceResolver:
    """Resolve embedding service from resolved config with global fallback."""

    def __init__(
        self,
        settings: Settings,
        provider_api_key_crypto_service: ProviderApiKeyCryptoService,
        default_embedding_service: EmbeddingService | None = None,
    ) -> None:
        self._settings = settings
        self._provider_api_key_crypto_service = provider_api_key_crypto_service
        self._default_embedding_service = default_embedding_service

    def resolve(
        self,
        backend: str | None,
        model: str | None,
        encrypted_api_key: str | None,
    ) -> EmbeddingService:
        effective_backend = backend or self._settings.default_embedding_provider

        if effective_backend == "openai":
            api_key = self._resolve_api_key(
                encrypted_api_key, self._resolve_default_api_key(effective_backend)
            )
            effective_model = model or self._resolve_default_model(effective_backend)
            return OpenAIEmbeddingService(
                api_key=api_key,
                model=effective_model,
                expected_dimension=self._settings.embedding_dimension,
            )

        if effective_backend == "gemini":
            api_key = self._resolve_api_key(
                encrypted_api_key, self._resolve_default_api_key(effective_backend)
            )
            effective_model = model or self._resolve_default_model(effective_backend)
            return GeminiEmbeddingService(
                api_key=api_key,
                model=effective_model,
                expected_dimension=self._settings.embedding_dimension,
            )

        if effective_backend == "ollama":
            effective_model = model or self._resolve_default_model(effective_backend)
            ollama_service = OllamaEmbeddingService(
                base_url=self._settings.ollama_base_url,
                model=effective_model,
                expected_dimension=self._settings.embedding_dimension,
            )
            return ContextualEmbeddingService(delegate=ollama_service)

        return (
            self._default_embedding_service
            if self._default_embedding_service is not None
            else InMemoryEmbeddingService(dimension=self._settings.embedding_dimension)
        )

    def _resolve_api_key(self, encrypted_api_key: str | None, fallback_api_key: str) -> str:
        if encrypted_api_key is None or encrypted_api_key.strip() == "":
            return fallback_api_key
        return self._provider_api_key_crypto_service.decrypt(encrypted_api_key)

    def _resolve_default_api_key(self, backend: str) -> str:
        if backend == self._settings.default_embedding_provider:
            return self._settings.default_embedding_api_key
        return ""

    def _resolve_default_model(self, backend: str) -> str:
        if backend == self._settings.default_embedding_provider:
            return self._settings.default_embedding_model
        return ""
