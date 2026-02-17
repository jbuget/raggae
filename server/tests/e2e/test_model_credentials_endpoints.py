from uuid import uuid4

from httpx import AsyncClient


class TestModelCredentialsEndpoints:
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

    async def test_create_list_activate_delete_model_credentials(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        create_first = await client.post(
            "/api/v1/model-credentials",
            json={"provider": "openai", "api_key": "sk-first-1234"},
            headers=headers,
        )
        create_second = await client.post(
            "/api/v1/model-credentials",
            json={"provider": "openai", "api_key": "sk-second-5678"},
            headers=headers,
        )
        first_id = create_first.json()["id"]
        second_id = create_second.json()["id"]

        before_activate = await client.get("/api/v1/model-credentials", headers=headers)
        activate = await client.patch(
            f"/api/v1/model-credentials/{first_id}/activate",
            headers=headers,
        )
        after_activate = await client.get("/api/v1/model-credentials", headers=headers)
        delete = await client.delete(f"/api/v1/model-credentials/{second_id}", headers=headers)
        after_delete = await client.get("/api/v1/model-credentials", headers=headers)

        # Then
        assert create_first.status_code == 201
        assert create_second.status_code == 201
        assert create_first.json()["masked_key"] == "...1234"
        assert create_second.json()["masked_key"] == "...5678"

        assert before_activate.status_code == 200
        before_data = before_activate.json()
        assert len(before_data) == 2
        assert len([item for item in before_data if item["is_active"]]) == 1

        assert activate.status_code == 204

        assert after_activate.status_code == 200
        after_data = after_activate.json()
        assert len(after_data) == 2
        assert len([item for item in after_data if item["is_active"]]) == 1
        first = next(item for item in after_data if item["id"] == first_id)
        assert first["is_active"] is True

        assert delete.status_code == 204
        assert after_delete.status_code == 200
        assert len(after_delete.json()) == 1

    async def test_activate_model_credential_of_another_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        owner_headers = await self._auth_headers(client)
        other_headers = await self._auth_headers(client)
        create_response = await client.post(
            "/api/v1/model-credentials",
            json={"provider": "gemini", "api_key": "AIza-owner-1234"},
            headers=owner_headers,
        )
        credential_id = create_response.json()["id"]

        # When
        response = await client.patch(
            f"/api/v1/model-credentials/{credential_id}/activate",
            headers=other_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_create_model_credential_without_access_token_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        # When
        response = await client.post(
            "/api/v1/model-credentials",
            json={"provider": "anthropic", "api_key": "sk-ant-test-1234"},
        )

        # Then
        assert response.status_code == 401
