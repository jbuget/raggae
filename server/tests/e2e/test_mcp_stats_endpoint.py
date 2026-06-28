from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from httpx import AsyncClient

from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot


class _FakeUrlSafetyValidator:
    async def validate(self, _url: str) -> None:
        return None


class _FakeMcpClient:
    async def list_tools(self, url: str, bearer_token: str | None = None) -> list[McpToolSnapshot]:
        return [McpToolSnapshot(name="search", description="", input_schema={})]

    async def call_tool(self, *args: object, **kwargs: object) -> dict[str, object]:
        return {}


@pytest.fixture
async def fake_mcp_services() -> AsyncIterator[None]:
    from raggae.presentation.api import dependencies

    original_validator = dependencies._url_safety_validator
    original_client = dependencies._mcp_client
    dependencies._url_safety_validator = _FakeUrlSafetyValidator()
    dependencies._mcp_client = _FakeMcpClient()
    try:
        yield
    finally:
        dependencies._url_safety_validator = original_validator
        dependencies._mcp_client = original_client


class TestMcpStatsEndpoint:
    async def _auth_headers(self, client: AsyncClient) -> dict[str, str]:
        unique = uuid4().hex
        email = f"{unique}@example.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "full_name": "MCP Stats User",
            },
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass123!"},
        )
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    async def test_returns_zeros_when_no_mcp_data(self, client: AsyncClient, fake_mcp_services: None) -> None:
        headers = await self._auth_headers(client)
        response = await client.get("/api/v1/stats/mcp", headers=headers)

        assert response.status_code == 200
        body = response.json()
        assert body == {
            "org_servers_total": 0,
            "org_servers_active": 0,
            "project_activations_active": 0,
            "projects_with_at_least_one_activation": 0,
        }

    async def test_counts_org_servers_and_activations(
        self, client: AsyncClient, fake_mcp_services: None
    ) -> None:
        headers = await self._auth_headers(client)
        # Setup: an org with one MCP declared
        org_response = await client.post(
            "/api/v1/organizations",
            json={"name": "Acme", "description": "stats test"},
            headers=headers,
        )
        org_id = org_response.json()["id"]
        declare = await client.post(
            f"/api/v1/organizations/{org_id}/mcp-servers",
            json={
                "name": "Notion",
                "url": "https://mcp.notion.test/",
                "auth_type": "none",
                "bearer_token": None,
                "timeout_seconds": 30,
            },
            headers=headers,
        )
        mcp_id = declare.json()["id"]
        project = await client.post(
            "/api/v1/projects",
            json={"name": "P", "description": "", "organization_id": org_id},
            headers=headers,
        )
        project_id = project.json()["id"]
        await client.post(
            f"/api/v1/projects/{project_id}/mcp-activations/{mcp_id}",
            headers=headers,
        )

        response = await client.get("/api/v1/stats/mcp", headers=headers)
        body = response.json()
        assert body["org_servers_total"] == 1
        assert body["org_servers_active"] == 1
        assert body["project_activations_active"] == 1
        assert body["projects_with_at_least_one_activation"] == 1
