from httpx import AsyncClient


class TestHealth:
    async def test_health_endpoint_returns_ok(self, client: AsyncClient) -> None:
        # When
        response = await client.get("/health")

        # Then
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
