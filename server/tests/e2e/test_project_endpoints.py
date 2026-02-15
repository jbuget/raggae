from uuid import uuid4

from httpx import AsyncClient


class TestProjectEndpoints:
    async def test_create_project_returns_201(self, client: AsyncClient) -> None:
        # Given
        user_id = str(uuid4())

        # When
        response = await client.post(
            f"/api/v1/projects?user_id={user_id}",
            json={
                "name": "My Project",
                "description": "A test project",
                "system_prompt": "You are a helpful assistant",
            },
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Project"
        assert data["description"] == "A test project"
        assert data["system_prompt"] == "You are a helpful assistant"
        assert data["user_id"] == user_id
        assert data["is_published"] is False
        assert "id" in data

    async def test_get_project_returns_200(self, client: AsyncClient) -> None:
        # Given
        user_id = str(uuid4())
        create_response = await client.post(
            f"/api/v1/projects?user_id={user_id}",
            json={"name": "Test Project"},
        )
        project_id = create_response.json()["id"]

        # When
        response = await client.get(f"/api/v1/projects/{project_id}")

        # Then
        assert response.status_code == 200
        assert response.json()["name"] == "Test Project"

    async def test_get_project_not_found_returns_404(self, client: AsyncClient) -> None:
        # When
        response = await client.get(f"/api/v1/projects/{uuid4()}")

        # Then
        assert response.status_code == 404

    async def test_list_projects_returns_200(self, client: AsyncClient) -> None:
        # Given
        user_id = str(uuid4())
        await client.post(
            f"/api/v1/projects?user_id={user_id}",
            json={"name": "Project 1"},
        )
        await client.post(
            f"/api/v1/projects?user_id={user_id}",
            json={"name": "Project 2"},
        )

        # When
        response = await client.get(f"/api/v1/projects?user_id={user_id}")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    async def test_delete_project_returns_204(self, client: AsyncClient) -> None:
        # Given
        user_id = str(uuid4())
        create_response = await client.post(
            f"/api/v1/projects?user_id={user_id}",
            json={"name": "To Delete"},
        )
        project_id = create_response.json()["id"]

        # When
        response = await client.delete(f"/api/v1/projects/{project_id}")

        # Then
        assert response.status_code == 204

    async def test_delete_project_not_found_returns_404(self, client: AsyncClient) -> None:
        # When
        response = await client.delete(f"/api/v1/projects/{uuid4()}")

        # Then
        assert response.status_code == 404
