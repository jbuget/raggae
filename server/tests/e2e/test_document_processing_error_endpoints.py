import importlib
from uuid import uuid4

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError


class TestDocumentProcessingErrorEndpoints:
    async def _client_with_sync_mode(
        self,
        monkeypatch,
    ) -> tuple[AsyncClient, object]:
        monkeypatch.setenv("PROCESSING_MODE", "sync")
        monkeypatch.setenv("EMBEDDING_BACKEND", "inmemory")
        monkeypatch.setenv("STORAGE_BACKEND", "inmemory")
        monkeypatch.setenv("PERSISTENCE_BACKEND", "inmemory")

        from raggae.infrastructure.config import settings as settings_module
        from raggae.presentation.api import dependencies
        from raggae.presentation.api.v1.endpoints import auth, documents, projects

        importlib.reload(settings_module)
        importlib.reload(dependencies)
        reloaded_auth = importlib.reload(auth)
        reloaded_projects = importlib.reload(projects)
        reloaded_documents = importlib.reload(documents)

        app = FastAPI(
            title="Raggae",
            description="RAG Generator Agent Expert",
            version="0.1.0",
        )
        app.include_router(reloaded_auth.router, prefix="/api/v1")
        app.include_router(reloaded_projects.router, prefix="/api/v1")
        app.include_router(reloaded_documents.router, prefix="/api/v1")

        transport = ASGITransport(app=app)
        client = AsyncClient(transport=transport, base_url="http://test")
        return client, dependencies

    async def _auth_headers(self, client: AsyncClient) -> dict[str, str]:
        unique = uuid4().hex
        email = f"{unique}@example.com"

        await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "full_name": "Test User",
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": "SecurePass123!",
            },
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    async def _create_project(self, client: AsyncClient) -> tuple[dict[str, str], str]:
        headers = await self._auth_headers(client)
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Processing Errors"},
            headers=headers,
        )
        return headers, response.json()["id"]

    async def test_upload_doc_in_sync_mode_returns_processing_error_in_batch_payload(
        self,
        monkeypatch,
    ) -> None:
        # Given
        client, _ = await self._client_with_sync_mode(monkeypatch)
        headers, project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/documents",
            files=[("files", ("legacy.doc", b"binary-doc", "application/msword"))],
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["failed"] == 1
        assert data["errors"][0]["code"] == "PROCESSING_FAILED"
        await client.aclose()

    async def test_upload_txt_in_sync_mode_returns_embedding_error_in_batch_payload(
        self,
        monkeypatch,
    ) -> None:
        # Given
        client, dependencies = await self._client_with_sync_mode(monkeypatch)

        async def raise_embedding_error(_: list[str]) -> list[list[float]]:
            raise EmbeddingGenerationError("embedding provider unavailable")

        monkeypatch.setattr(
            dependencies._embedding_service,
            "embed_texts",
            raise_embedding_error,
        )
        headers, project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/documents",
            files=[("files", ("notes.txt", b"hello", "text/plain"))],
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["failed"] == 1
        assert data["errors"][0]["code"] == "PROCESSING_FAILED"
        await client.aclose()
