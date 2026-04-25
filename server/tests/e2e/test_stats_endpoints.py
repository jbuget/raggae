from uuid import uuid4

from httpx import AsyncClient


class TestStatsEndpoints:
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

    async def test_e2e_stats_returns_401_without_authentication(self, client: AsyncClient) -> None:
        # When
        response = await client.get("/api/v1/stats")

        # Then
        assert response.status_code == 401

    async def test_e2e_stats_returns_200_with_authentication(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.get("/api/v1/stats", headers=headers)

        # Then
        assert response.status_code == 200

    async def test_e2e_stats_response_has_expected_structure(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.get("/api/v1/stats", headers=headers)

        # Then
        data = response.json()
        assert "generated_at" in data
        assert "north_star_reliable_answers" in data
        assert "fonctionnement" in data
        assert "usage" in data
        assert "impact" in data

    async def test_e2e_stats_fonctionnement_has_expected_fields(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.get("/api/v1/stats", headers=headers)

        # Then
        fonctionnement = response.json()["fonctionnement"]
        assert "indexing_success_rate_percent" in fonctionnement
        assert "projects_with_documents" in fonctionnement
        assert "total_document_size_mb" in fonctionnement
        assert "total_chunks" in fonctionnement

    async def test_e2e_stats_usage_has_expected_fields(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.get("/api/v1/stats", headers=headers)

        # Then
        usage = response.json()["usage"]
        assert "users_total" in usage
        assert "users_active_30d" in usage
        assert "organizations_total" in usage
        assert "projects_total" in usage
        assert "projects_published" in usage
        assert "conversations_total" in usage
        assert "messages_total" in usage
        assert "documents_total" in usage

    async def test_e2e_stats_impact_has_expected_fields(self, client: AsyncClient) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.get("/api/v1/stats", headers=headers)

        # Then
        impact = response.json()["impact"]
        assert "reliable_answers_total" in impact
        assert "average_reliability_percent" in impact
        assert "relevant_answers_rate_percent" in impact
        assert "multi_turn_conversations_rate_percent" in impact
        assert "average_sources_per_answer" in impact

    async def test_e2e_stats_north_star_equals_reliable_answers_total(
        self, client: AsyncClient
    ) -> None:
        # Given
        headers = await self._auth_headers(client)

        # When
        response = await client.get("/api/v1/stats", headers=headers)

        # Then
        data = response.json()
        assert data["north_star_reliable_answers"] == data["impact"]["reliable_answers_total"]

    async def test_e2e_stats_returns_zero_values_on_empty_database(
        self, client: AsyncClient
    ) -> None:
        # Given — empty in-memory database (default test setup)
        headers = await self._auth_headers(client)

        # When
        response = await client.get("/api/v1/stats", headers=headers)

        # Then
        data = response.json()
        assert data["north_star_reliable_answers"] == 0
        assert data["usage"]["users_total"] == 0
        assert data["usage"]["conversations_total"] == 0
