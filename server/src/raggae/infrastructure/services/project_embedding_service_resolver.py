from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.application.interfaces.services.provider_api_key_crypto_service import (
    ProviderApiKeyCryptoService,
)
from raggae.domain.entities.project import Project
from raggae.infrastructure.config.settings import Settings
from raggae.infrastructure.services.gemini_embedding_service import GeminiEmbeddingService
from raggae.infrastructure.services.in_memory_embedding_service import InMemoryEmbeddingService
from raggae.infrastructure.services.ollama_embedding_service import OllamaEmbeddingService
from raggae.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService


class ProjectEmbeddingServiceResolver:
    """Resolve embedding service using project settings with global fallback."""

    def __init__(
        self,
        settings: Settings,
        provider_api_key_crypto_service: ProviderApiKeyCryptoService,
        default_embedding_service: EmbeddingService | None = None,
    ) -> None:
        self._settings = settings
        self._provider_api_key_crypto_service = provider_api_key_crypto_service
        self._default_embedding_service = default_embedding_service

    def resolve(self, project: Project) -> EmbeddingService:
        backend = project.embedding_backend or self._settings.default_embedding_provider

        if backend == "openai":
            api_key = self._resolve_api_key(
                encrypted_api_key=project.embedding_api_key_encrypted,
                fallback_api_key=self._resolve_default_api_key(backend),
            )
            model = project.embedding_model or self._resolve_default_model(backend)
            return OpenAIEmbeddingService(
                api_key=api_key,
                model=model,
                expected_dimension=self._settings.embedding_dimension,
            )

        if backend == "gemini":
            api_key = self._resolve_api_key(
                encrypted_api_key=project.embedding_api_key_encrypted,
                fallback_api_key=self._resolve_default_api_key(backend),
            )
            model = project.embedding_model or self._resolve_default_model(backend)
            return GeminiEmbeddingService(
                api_key=api_key,
                model=model,
                expected_dimension=self._settings.embedding_dimension,
            )

        if backend == "ollama":
            model = project.embedding_model or self._resolve_default_model(backend)
            return OllamaEmbeddingService(
                base_url=self._settings.ollama_base_url,
                model=model,
                expected_dimension=self._settings.embedding_dimension,
            )

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
