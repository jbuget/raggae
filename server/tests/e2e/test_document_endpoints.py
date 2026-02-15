from uuid import uuid4

from httpx import AsyncClient


class TestDocumentEndpoints:
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
            json={"name": "Project Documents"},
            headers=headers,
        )
        return headers, response.json()["id"]

    async def test_upload_document_returns_201(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/documents",
            files={"file": ("notes.txt", b"hello", "text/plain")},
            headers=headers,
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == project_id
        assert data["file_name"] == "notes.txt"

    async def test_list_project_documents_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        await client.post(
            f"/api/v1/projects/{project_id}/documents",
            files={"file": ("guide.md", b"# Guide", "text/markdown")},
            headers=headers,
        )

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/documents",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["file_name"] == "guide.md"

    async def test_delete_document_returns_204(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        upload_response = await client.post(
            f"/api/v1/projects/{project_id}/documents",
            files={"file": ("to-delete.pdf", b"pdf-content", "application/pdf")},
            headers=headers,
        )
        document_id = upload_response.json()["id"]

        # When
        response = await client.delete(
            f"/api/v1/projects/{project_id}/documents/{document_id}",
            headers=headers,
        )

        # Then
        assert response.status_code == 204

    async def test_list_document_chunks_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        upload_response = await client.post(
            f"/api/v1/projects/{project_id}/documents",
            files={"file": ("notes.txt", b"hello world", "text/plain")},
            headers=headers,
        )
        document_id = upload_response.json()["id"]

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/documents/{document_id}/chunks",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_document_chunks_of_another_user_project_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        owner_headers, project_id = await self._create_project(client)
        upload_response = await client.post(
            f"/api/v1/projects/{project_id}/documents",
            files={"file": ("private.txt", b"secret", "text/plain")},
            headers=owner_headers,
        )
        document_id = upload_response.json()["id"]
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/documents/{document_id}/chunks",
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_upload_document_of_another_user_project_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        _, project_id = await self._create_project(client)
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/documents",
            files={"file": ("notes.txt", b"hello", "text/plain")},
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404
