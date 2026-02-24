from raggae.application.interfaces.services.llm_service import LLMService
from raggae.application.interfaces.services.provider_api_key_crypto_service import (
    ProviderApiKeyCryptoService,
)
from raggae.domain.entities.project import Project
from raggae.infrastructure.config.settings import Settings
from raggae.infrastructure.services.gemini_llm_service import GeminiLLMService
from raggae.infrastructure.services.in_memory_llm_service import InMemoryLLMService
from raggae.infrastructure.services.ollama_llm_service import OllamaLLMService
from raggae.infrastructure.services.openai_llm_service import OpenAILLMService


class ProjectLLMServiceResolver:
    """Resolve llm service using project settings with global fallback."""

    def __init__(
        self,
        settings: Settings,
        provider_api_key_crypto_service: ProviderApiKeyCryptoService,
        default_llm_service: LLMService | None = None,
    ) -> None:
        self._settings = settings
        self._provider_api_key_crypto_service = provider_api_key_crypto_service
        self._default_llm_service = default_llm_service

    def resolve(self, project: Project) -> LLMService:
        backend = project.llm_backend or self._settings.llm_backend

        if backend == "openai":
            api_key = self._resolve_api_key(
                encrypted_api_key=project.llm_api_key_encrypted,
                fallback_api_key=self._settings.openai_api_key,
            )
            model = project.llm_model or self._settings.openai_llm_model
            return OpenAILLMService(api_key=api_key, model=model)

        if backend == "gemini":
            api_key = self._resolve_api_key(
                encrypted_api_key=project.llm_api_key_encrypted,
                fallback_api_key=self._settings.gemini_api_key,
            )
            model = project.llm_model or self._settings.gemini_llm_model
            return GeminiLLMService(api_key=api_key, model=model)

        if backend == "ollama":
            model = project.llm_model or self._settings.ollama_llm_model
            return OllamaLLMService(
                base_url=self._settings.ollama_base_url,
                model=model,
                timeout_seconds=self._settings.llm_request_timeout_seconds,
                keep_alive=self._settings.ollama_keep_alive,
            )

        return (
            self._default_llm_service
            if self._default_llm_service is not None
            else InMemoryLLMService()
        )

    def _resolve_api_key(self, encrypted_api_key: str | None, fallback_api_key: str) -> str:
        if encrypted_api_key is None or encrypted_api_key.strip() == "":
            return fallback_api_key
        return self._provider_api_key_crypto_service.decrypt(encrypted_api_key)
