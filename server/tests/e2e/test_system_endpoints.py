import pytest
from httpx import AsyncClient


class TestSystemDefaultsEndpoint:
    async def test_get_system_defaults_returns_200(self, client: AsyncClient) -> None:
        # Given / When
        response = await client.get("/api/v1/system/defaults")

        # Then
        assert response.status_code == 200

    async def test_get_system_defaults_returns_expected_fields(self, client: AsyncClient) -> None:
        # Given / When
        response = await client.get("/api/v1/system/defaults")

        # Then
        data = response.json()
        assert "llm_backend" in data
        assert "llm_model" in data
        assert "embedding_backend" in data
        assert "embedding_model" in data
        assert "retrieval_strategy" in data
        assert "retrieval_top_k" in data
        assert "retrieval_min_score" in data

    async def test_get_system_defaults_normalizes_provider_to_lowercase(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given — env vars with mixed case (as users often configure them)
        monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "Gemini")
        monkeypatch.setenv("DEFAULT_EMBEDDING_PROVIDER", "OpenAI")

        # Reload settings after env change
        import importlib

        import raggae.infrastructure.config.settings as settings_module
        import raggae.presentation.api.v1.endpoints.system as system_module

        importlib.reload(settings_module)
        importlib.reload(system_module)

        # When
        response = await client.get("/api/v1/system/defaults")

        # Then
        data = response.json()
        assert data["llm_backend"] == data["llm_backend"].lower()
        assert data["embedding_backend"] == data["embedding_backend"].lower()

    async def test_get_system_defaults_backends_are_always_lowercase(self, client: AsyncClient) -> None:
        # Given / When
        response = await client.get("/api/v1/system/defaults")

        # Then — regardless of env var casing, backends must be lowercase
        data = response.json()
        assert data["llm_backend"] == data["llm_backend"].lower()
        assert data["embedding_backend"] == data["embedding_backend"].lower()
        assert data["reranker_backend"] == data["reranker_backend"].lower()

    async def test_get_system_defaults_retrieval_top_k_is_positive_integer(self, client: AsyncClient) -> None:
        # Given / When
        response = await client.get("/api/v1/system/defaults")

        # Then
        data = response.json()
        assert isinstance(data["retrieval_top_k"], int)
        assert data["retrieval_top_k"] > 0

    async def test_get_system_defaults_retrieval_min_score_is_between_0_and_1(
        self, client: AsyncClient
    ) -> None:
        # Given / When
        response = await client.get("/api/v1/system/defaults")

        # Then
        data = response.json()
        assert 0.0 <= data["retrieval_min_score"] <= 1.0
