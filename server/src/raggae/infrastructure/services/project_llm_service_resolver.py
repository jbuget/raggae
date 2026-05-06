from raggae.application.interfaces.services.llm_service import LLMService
from raggae.application.interfaces.services.provider_api_key_crypto_service import (
    ProviderApiKeyCryptoService,
)
from raggae.infrastructure.config.settings import Settings
from raggae.infrastructure.services.gemini_llm_service import GeminiLLMService
from raggae.infrastructure.services.in_memory_llm_service import InMemoryLLMService
from raggae.infrastructure.services.ollama_llm_service import OllamaLLMService
from raggae.infrastructure.services.openai_llm_service import OpenAILLMService


class ProjectLLMServiceResolver:
    """Resolve LLM service from resolved config with global fallback."""

    def __init__(
        self,
        settings: Settings,
        provider_api_key_crypto_service: ProviderApiKeyCryptoService,
        default_llm_service: LLMService | None = None,
    ) -> None:
        self._settings = settings
        self._provider_api_key_crypto_service = provider_api_key_crypto_service
        self._default_llm_service = default_llm_service

    def resolve(
        self,
        backend: str | None,
        model: str | None,
        encrypted_api_key: str | None,
    ) -> LLMService:
        effective_backend = backend or self._settings.default_llm_provider

        if effective_backend == "openai":
            api_key = self._resolve_api_key(encrypted_api_key, self._resolve_default_api_key(effective_backend))
            effective_model = model or self._resolve_default_model(effective_backend)
            return OpenAILLMService(api_key=api_key, model=effective_model)

        if effective_backend == "gemini":
            api_key = self._resolve_api_key(encrypted_api_key, self._resolve_default_api_key(effective_backend))
            effective_model = model or self._resolve_default_model(effective_backend)
            return GeminiLLMService(api_key=api_key, model=effective_model)

        if effective_backend == "ollama":
            effective_model = model or self._resolve_default_model(effective_backend)
            return OllamaLLMService(
                base_url=self._settings.ollama_base_url,
                model=effective_model,
                timeout_seconds=self._settings.llm_request_timeout_seconds,
                keep_alive=self._settings.ollama_keep_alive,
            )

        return self._default_llm_service if self._default_llm_service is not None else InMemoryLLMService()

    def _resolve_api_key(self, encrypted_api_key: str | None, fallback_api_key: str) -> str:
        if encrypted_api_key is None or encrypted_api_key.strip() == "":
            return fallback_api_key
        return self._provider_api_key_crypto_service.decrypt(encrypted_api_key)

    def _resolve_default_api_key(self, backend: str) -> str:
        if backend == self._settings.default_llm_provider:
            return self._settings.default_llm_api_key
        return ""

    def _resolve_default_model(self, backend: str) -> str:
        if backend == self._settings.default_llm_provider:
            return self._settings.default_llm_model
        return ""
