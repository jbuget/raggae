from uuid import uuid4

from httpx import AsyncClient


class TestOrganizationDefaultConfigEndpoints:
    async def _auth_headers(self, client: AsyncClient) -> dict[str, str]:
        unique = uuid4().hex
        email = f"{unique}@example.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "SecurePass123!", "full_name": "Config User"},
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass123!"},
        )
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    async def _create_org(self, client: AsyncClient, headers: dict[str, str]) -> str:
        create = await client.post(
            "/api/v1/organizations",
            json={"name": "Config Org"},
            headers=headers,
        )
        assert create.status_code == 201
        return create.json()["id"]

    async def test_e2e_get_default_config_returns_null_when_not_set(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)

        # When
        response = await client.get(
            f"/api/v1/organizations/{org_id}/default-config",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        assert response.json() is None

    async def test_e2e_upsert_creates_default_config(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)

        # When
        response = await client.put(
            f"/api/v1/organizations/{org_id}/default-config",
            json={
                "embedding_backend": "openai",
                "llm_backend": "openai",
                "chunking_strategy": "paragraph",
                "retrieval_strategy": "hybrid",
                "retrieval_top_k": 10,
                "retrieval_min_score": 0.4,
                "reranking_enabled": False,
                "reranker_backend": None,
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["embedding_backend"] == "openai"
        assert data["llm_backend"] == "openai"
        assert data["chunking_strategy"] == "paragraph"
        assert data["retrieval_strategy"] == "hybrid"
        assert data["retrieval_top_k"] == 10
        assert data["organization_id"] == org_id

    async def test_e2e_upsert_updates_existing_config(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)
        await client.put(
            f"/api/v1/organizations/{org_id}/default-config",
            json={"embedding_backend": "openai"},
            headers=headers,
        )

        # When
        response = await client.put(
            f"/api/v1/organizations/{org_id}/default-config",
            json={"embedding_backend": "gemini", "llm_backend": "gemini"},
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["embedding_backend"] == "gemini"
        assert data["llm_backend"] == "gemini"

        # And the id stays the same (upsert, not recreate)
        first_id = (
            await client.get(f"/api/v1/organizations/{org_id}/default-config", headers=headers)
        ).json()["id"]
        assert data["id"] == first_id

    async def test_e2e_get_after_upsert_returns_config(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)
        await client.put(
            f"/api/v1/organizations/{org_id}/default-config",
            json={"llm_backend": "openai", "chunking_strategy": "auto"},
            headers=headers,
        )

        # When
        response = await client.get(
            f"/api/v1/organizations/{org_id}/default-config",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["llm_backend"] == "openai"
        assert data["chunking_strategy"] == "auto"

    async def test_e2e_get_returns_403_for_unauthenticated(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)

        # When
        response = await client.get(f"/api/v1/organizations/{org_id}/default-config")

        # Then
        assert response.status_code == 401

    async def test_e2e_put_returns_403_for_unauthenticated(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)

        # When
        response = await client.put(
            f"/api/v1/organizations/{org_id}/default-config",
            json={"embedding_backend": "openai"},
        )

        # Then
        assert response.status_code == 401

    async def test_e2e_get_returns_404_for_unknown_org(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        unknown_id = str(uuid4())

        # When
        response = await client.get(
            f"/api/v1/organizations/{unknown_id}/default-config",
            headers=headers,
        )

        # Then
        assert response.status_code == 404

    async def test_e2e_put_returns_404_for_unknown_org(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        unknown_id = str(uuid4())

        # When
        response = await client.put(
            f"/api/v1/organizations/{unknown_id}/default-config",
            json={"embedding_backend": "openai"},
            headers=headers,
        )

        # Then
        assert response.status_code == 404
