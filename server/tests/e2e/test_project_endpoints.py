from uuid import uuid4

from httpx import AsyncClient


class TestProjectEndpoints:
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

    async def _create_project_as_authenticated_user(
        self,
        client: AsyncClient,
        name: str,
    ) -> tuple[dict[str, str], str]:
        headers = await self._auth_headers(client)
        response = await client.post(
            "/api/v1/projects",
            json={"name": name},
            headers=headers,
        )
        project_id = response.json()["id"]
        return headers, project_id

    async def test_create_project_returns_201(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "My Project",
                "description": "A test project",
                "system_prompt": "You are a helpful assistant",
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Project"
        assert data["description"] == "A test project"
        assert data["system_prompt"] == "You are a helpful assistant"
        assert "user_id" in data
        assert data["is_published"] is False
        assert "id" in data

    async def test_get_project_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        create_response = await client.post(
            "/api/v1/projects",
            json={"name": "Test Project"},
            headers=headers,
        )
        project_id = create_response.json()["id"]

        # When
        response = await client.get(f"/api/v1/projects/{project_id}", headers=headers)

        # Then
        assert response.status_code == 200
        assert response.json()["name"] == "Test Project"

    async def test_get_project_not_found_returns_404(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.get(f"/api/v1/projects/{uuid4()}", headers=headers)

        # Then
        assert response.status_code == 404

    async def test_list_projects_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        await client.post(
            "/api/v1/projects",
            json={"name": "Project 1"},
            headers=headers,
        )
        await client.post(
            "/api/v1/projects",
            json={"name": "Project 2"},
            headers=headers,
        )

        # When
        response = await client.get("/api/v1/projects", headers=headers)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    async def test_delete_project_returns_204(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)
        create_response = await client.post(
            "/api/v1/projects",
            json={"name": "To Delete"},
            headers=headers,
        )
        project_id = create_response.json()["id"]

        # When
        response = await client.delete(f"/api/v1/projects/{project_id}", headers=headers)

        # Then
        assert response.status_code == 204

    async def test_delete_project_not_found_returns_404(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.delete(f"/api/v1/projects/{uuid4()}", headers=headers)

        # Then
        assert response.status_code == 404

    async def test_create_project_without_access_token_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        # When
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Unauthorized"},
        )

        # Then
        assert response.status_code == 401

    async def test_get_project_of_another_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        _, project_id = await self._create_project_as_authenticated_user(
            client=client,
            name="Owner Project",
        )
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_delete_project_of_another_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        _, project_id = await self._create_project_as_authenticated_user(
            client=client,
            name="Owner Project",
        )
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_update_project_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project_as_authenticated_user(
            client=client,
            name="Project to update",
        )

        # When
        response = await client.patch(
            f"/api/v1/projects/{project_id}",
            json={
                "name": "Updated project",
                "description": "Updated description",
                "system_prompt": "Updated prompt",
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == "Updated project"
        assert data["description"] == "Updated description"
        assert data["system_prompt"] == "Updated prompt"

    async def test_update_project_not_found_returns_404(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.patch(
            f"/api/v1/projects/{uuid4()}",
            json={
                "name": "Updated project",
                "description": "Updated description",
                "system_prompt": "Updated prompt",
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 404

    async def test_update_project_of_another_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        _, project_id = await self._create_project_as_authenticated_user(
            client=client,
            name="Owner Project",
        )
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.patch(
            f"/api/v1/projects/{project_id}",
            json={
                "name": "Updated project",
                "description": "Updated description",
                "system_prompt": "Updated prompt",
            },
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404
