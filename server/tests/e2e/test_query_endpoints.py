from uuid import uuid4

from httpx import AsyncClient


class TestQueryEndpoints:
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
            json={"name": "Project Query"},
            headers=headers,
        )
        return headers, response.json()["id"]

    async def test_query_project_chunks_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/query",
            json={"query": "hello", "limit": 3},
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == project_id
        assert data["query"] == "hello"
        assert isinstance(data["chunks"], list)

    async def test_query_project_chunks_of_another_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        _, project_id = await self._create_project(client)
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/query",
            json={"query": "hello", "limit": 3},
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_query_project_chunks_rejects_invalid_limit(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/query",
            json={"query": "hello", "limit": 0},
            headers=headers,
        )

        # Then
        assert response.status_code == 422
