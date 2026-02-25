from httpx import AsyncClient


class TestAuthEndpoints:
    async def _register_and_login(self, client: AsyncClient, email: str) -> str:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "full_name": "Test User",
            },
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": "SecurePass123!",
            },
        )
        return login.json()["access_token"]

    async def test_register_user_returns_201(self, client: AsyncClient) -> None:
        # When
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "full_name": "Test User",
            },
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_register_duplicate_email_returns_409(self, client: AsyncClient) -> None:
        # Given
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "dup@example.com",
                "password": "SecurePass123!",
                "full_name": "First",
            },
        )

        # When
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "dup@example.com",
                "password": "SecurePass123!",
                "full_name": "Second",
            },
        )

        # Then
        assert response.status_code == 409

    async def test_login_returns_token(self, client: AsyncClient) -> None:
        # Given
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "SecurePass123!",
                "full_name": "Login User",
            },
        )

        # When
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "SecurePass123!",
            },
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password_returns_401(self, client: AsyncClient) -> None:
        # Given
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@example.com",
                "password": "SecurePass123!",
                "full_name": "User",
            },
        )

        # When
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongPass456!",
            },
        )

        # Then
        assert response.status_code == 401

    async def test_get_current_user_returns_profile(self, client: AsyncClient) -> None:
        token = await self._register_and_login(client, "me@example.com")

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"
        assert response.json()["full_name"] == "Test User"

    async def test_update_user_full_name_updates_profile(self, client: AsyncClient) -> None:
        token = await self._register_and_login(client, "update-name@example.com")

        update_response = await client.patch(
            "/api/v1/auth/me/full-name",
            json={"full_name": "Updated Name"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert update_response.status_code == 200
        assert update_response.json()["full_name"] == "Updated Name"

        profile_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert profile_response.status_code == 200
        assert profile_response.json()["full_name"] == "Updated Name"
