from uuid import uuid4

from httpx import AsyncClient


class TestModelCatalogEndpoints:
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

    async def test_get_model_catalog_returns_200(self, client: AsyncClient) -> None:
        headers = await self._auth_headers(client)

        response = await client.get("/api/v1/model-catalog", headers=headers)

        assert response.status_code == 200
        payload = response.json()
        assert "embedding" in payload
        assert "llm" in payload
        assert "openai" in payload["embedding"]
        assert "gemini" in payload["embedding"]
        assert "openai" in payload["llm"]
        assert "anthropic" in payload["llm"]

    async def test_get_model_catalog_without_access_token_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/model-catalog")
        assert response.status_code == 401
