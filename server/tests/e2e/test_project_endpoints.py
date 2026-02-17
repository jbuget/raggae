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

    async def _create_model_credential(
        self,
        client: AsyncClient,
        headers: dict[str, str],
        provider: str,
        api_key: str,
    ) -> str:
        response = await client.post(
            "/api/v1/model-credentials",
            json={"provider": provider, "api_key": api_key},
            headers=headers,
        )
        return response.json()["id"]

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
        assert data["chunking_strategy"] == "auto"
        assert data["parent_child_chunking"] is False
        assert "id" in data

    async def test_create_project_with_chunking_settings_returns_201(
        self, client: AsyncClient
    ) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "My Project",
                "description": "A test project",
                "system_prompt": "You are a helpful assistant",
                "chunking_strategy": "semantic",
                "parent_child_chunking": True,
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["chunking_strategy"] == "semantic"
        assert data["parent_child_chunking"] is True

    async def test_create_project_with_non_owned_llm_api_key_returns_422(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "My Project",
                "description": "A test project",
                "system_prompt": "You are a helpful assistant",
                "llm_backend": "openai",
                "llm_model": "gpt-4o-mini",
                "llm_api_key": "sk-not-owned-1234",
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 422
        assert "not registered for this user" in response.json()["detail"]

    async def test_create_project_with_owned_llm_api_key_returns_201(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers = await self._auth_headers(client)
        await self._create_model_credential(
            client=client,
            headers=headers,
            provider="openai",
            api_key="sk-owned-1234",
        )

        # When
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "My Project",
                "description": "A test project",
                "system_prompt": "You are a helpful assistant",
                "llm_backend": "openai",
                "llm_model": "gpt-4o-mini",
                "llm_api_key": "sk-owned-1234",
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["llm_backend"] == "openai"
        assert data["llm_model"] == "gpt-4o-mini"
        assert data["llm_api_key_masked"] is not None

    async def test_create_project_with_llm_api_key_credential_id_returns_201(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers = await self._auth_headers(client)
        credential_id = await self._create_model_credential(
            client=client,
            headers=headers,
            provider="openai",
            api_key="sk-owned-by-id-1234",
        )

        # When
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "My Project",
                "description": "A test project",
                "system_prompt": "You are a helpful assistant",
                "llm_backend": "openai",
                "llm_model": "gpt-4o-mini",
                "llm_api_key_credential_id": credential_id,
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["llm_backend"] == "openai"
        assert data["llm_model"] == "gpt-4o-mini"
        assert data["llm_api_key_masked"] is not None

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

    async def test_update_project_chunking_settings_returns_200(self, client: AsyncClient) -> None:
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
                "chunking_strategy": "semantic",
                "parent_child_chunking": True,
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["chunking_strategy"] == "semantic"
        assert data["parent_child_chunking"] is True

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

    async def test_reindex_project_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project_as_authenticated_user(
            client=client,
            name="Project to reindex",
        )

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/reindex",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == project_id
        assert data["total_documents"] == 0
        assert data["indexed_documents"] == 0
        assert data["failed_documents"] == 0

    async def test_update_project_with_llm_api_key_credential_id_returns_200(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers, project_id = await self._create_project_as_authenticated_user(
            client=client,
            name="Project to update",
        )
        credential_id = await self._create_model_credential(
            client=client,
            headers=headers,
            provider="openai",
            api_key="sk-update-by-id-1234",
        )

        # When
        response = await client.patch(
            f"/api/v1/projects/{project_id}",
            json={
                "name": "Updated project",
                "description": "Updated description",
                "system_prompt": "Updated prompt",
                "llm_backend": "openai",
                "llm_model": "gpt-4o-mini",
                "llm_api_key_credential_id": credential_id,
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["llm_backend"] == "openai"
        assert data["llm_api_key_masked"] is not None
