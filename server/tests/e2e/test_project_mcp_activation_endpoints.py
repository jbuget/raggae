from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from httpx import AsyncClient

from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot


class _FakeUrlSafetyValidator:
    async def validate(self, _url: str) -> None:
        return None


class _FakeMcpClient:
    def __init__(self) -> None:
        self.tools = [McpToolSnapshot(name="search", description="Search", input_schema={})]

    async def list_tools(self, url: str, bearer_token: str | None = None) -> list[McpToolSnapshot]:
        return list(self.tools)

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


class TestProjectMcpActivationEndpoints:
    async def _auth_headers(self, client: AsyncClient) -> dict[str, str]:
        unique = uuid4().hex
        email = f"{unique}@example.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "full_name": "MCP User",
            },
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass123!"},
        )
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    async def _create_org(self, client: AsyncClient, headers: dict[str, str]) -> str:
        response = await client.post(
            "/api/v1/organizations",
            json={"name": "Acme", "description": "MCP test"},
            headers=headers,
        )
        return response.json()["id"]

    async def _create_org_project(self, client: AsyncClient, headers: dict[str, str], org_id: str) -> str:
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "Project A",
                "description": "MCP project",
                "organization_id": org_id,
            },
            headers=headers,
        )
        assert response.status_code == 201, response.text
        return response.json()["id"]

    async def _declare_mcp(
        self,
        client: AsyncClient,
        headers: dict[str, str],
        org_id: str,
        slug: str = "notion",
    ) -> str:
        response = await client.post(
            f"/api/v1/organizations/{org_id}/mcp-servers",
            json={
                "name": slug.capitalize(),
                "url": f"https://mcp.{slug}.test/",
                "auth_type": "none",
                "bearer_token": None,
                "timeout_seconds": 30,
            },
            headers=headers,
        )
        assert response.status_code == 201, response.text
        return response.json()["id"]

    async def test_list_activate_deactivate_cycle(
        self,
        client: AsyncClient,
        fake_mcp_services: None,  # noqa: ARG002 — fixture only sets up state
    ) -> None:
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)
        project_id = await self._create_org_project(client, headers, org_id)
        mcp_id = await self._declare_mcp(client, headers, org_id)

        # Initially listed but not activated
        listed = await client.get(f"/api/v1/projects/{project_id}/mcp-activations", headers=headers)
        assert listed.status_code == 200
        views = listed.json()
        assert len(views) == 1
        assert views[0]["org_mcp_server"]["id"] == mcp_id
        assert views[0]["is_activated"] is False

        # Activate
        activate = await client.post(
            f"/api/v1/projects/{project_id}/mcp-activations/{mcp_id}", headers=headers
        )
        assert activate.status_code == 204

        after_activate = await client.get(f"/api/v1/projects/{project_id}/mcp-activations", headers=headers)
        assert after_activate.json()[0]["is_activated"] is True

        # Deactivate
        deactivate = await client.delete(
            f"/api/v1/projects/{project_id}/mcp-activations/{mcp_id}", headers=headers
        )
        assert deactivate.status_code == 204

        after_deactivate = await client.get(f"/api/v1/projects/{project_id}/mcp-activations", headers=headers)
        assert after_deactivate.json()[0]["is_activated"] is False

    async def test_inactive_org_mcp_is_hidden_from_listing(
        self,
        client: AsyncClient,
        fake_mcp_services: None,  # noqa: ARG002
    ) -> None:
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)
        project_id = await self._create_org_project(client, headers, org_id)
        mcp_id = await self._declare_mcp(client, headers, org_id)

        # Deactivate at org level
        await client.patch(
            f"/api/v1/organizations/{org_id}/mcp-servers/{mcp_id}/deactivate",
            headers=headers,
        )

        # The project no longer sees it
        listed = await client.get(f"/api/v1/projects/{project_id}/mcp-activations", headers=headers)
        assert listed.status_code == 200
        assert listed.json() == []

    async def test_activate_returns_403_when_server_is_inactive_at_org_level(
        self,
        client: AsyncClient,
        fake_mcp_services: None,  # noqa: ARG002
    ) -> None:
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)
        project_id = await self._create_org_project(client, headers, org_id)
        mcp_id = await self._declare_mcp(client, headers, org_id)
        await client.patch(
            f"/api/v1/organizations/{org_id}/mcp-servers/{mcp_id}/deactivate",
            headers=headers,
        )

        activate = await client.post(
            f"/api/v1/projects/{project_id}/mcp-activations/{mcp_id}", headers=headers
        )
        assert activate.status_code == 403

    async def test_user_without_access_to_project_gets_404(
        self,
        client: AsyncClient,
        fake_mcp_services: None,  # noqa: ARG002
    ) -> None:
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)
        project_id = await self._create_org_project(client, headers, org_id)
        await self._declare_mcp(client, headers, org_id)

        outsider_headers = await self._auth_headers(client)
        listed = await client.get(f"/api/v1/projects/{project_id}/mcp-activations", headers=outsider_headers)
        assert listed.status_code == 404
