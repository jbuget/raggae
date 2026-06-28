from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from httpx import AsyncClient

from raggae.domain.exceptions.mcp_exceptions import McpUrlForbiddenError
from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot


class _FakeUrlSafetyValidator:
    """Always accepts the URL — bypasses DNS in E2E tests."""

    def __init__(self) -> None:
        self.reject_urls: set[str] = set()

    async def validate(self, url: str) -> None:
        if url in self.reject_urls:
            raise McpUrlForbiddenError(f"URL '{url}' is on the test denylist")


class _FakeMcpClient:
    """Returns scripted snapshots so the handshake works deterministically."""

    def __init__(self) -> None:
        self.next_tools: list[McpToolSnapshot] = [
            McpToolSnapshot(
                name="search",
                description="Search documents",
                input_schema={"type": "object"},
            )
        ]

    async def list_tools(self, url: str, bearer_token: str | None = None) -> list[McpToolSnapshot]:
        return list(self.next_tools)

    async def call_tool(self, *args: object, **kwargs: object) -> dict[str, object]:
        return {"content": []}


@pytest.fixture
async def fake_mcp_services() -> AsyncIterator[tuple[_FakeUrlSafetyValidator, _FakeMcpClient]]:
    """Patch the module-level singletons used by the MCP use cases."""
    from raggae.presentation.api import dependencies

    original_validator = dependencies._url_safety_validator
    original_client = dependencies._mcp_client
    validator = _FakeUrlSafetyValidator()
    client = _FakeMcpClient()
    dependencies._url_safety_validator = validator
    dependencies._mcp_client = client
    try:
        yield validator, client
    finally:
        dependencies._url_safety_validator = original_validator
        dependencies._mcp_client = original_client


class TestOrgMcpServerEndpoints:
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
            json={"name": "Acme Org", "description": "MCP test org"},
            headers=headers,
        )
        assert response.status_code == 201
        return response.json()["id"]

    async def test_declare_list_refresh_update_activate_delete_flow(
        self,
        client: AsyncClient,
        fake_mcp_services: tuple[_FakeUrlSafetyValidator, _FakeMcpClient],
    ) -> None:
        # Given
        _, fake_client = fake_mcp_services
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)

        # When — declare
        declare = await client.post(
            f"/api/v1/organizations/{org_id}/mcp-servers",
            json={
                "name": "Notion",
                "url": "https://mcp.notion.test/",
                "auth_type": "bearer",
                "bearer_token": "secret-token-wxyz",
                "timeout_seconds": 20,
            },
            headers=headers,
        )

        # Then
        assert declare.status_code == 201
        body = declare.json()
        assert body["name"] == "Notion"
        assert body["slug"] == "notion"
        assert body["auth_type"] == "bearer"
        assert body["masked_token"] == "...wxyz"
        assert body["is_active"] is True
        assert body["timeout_seconds"] == 20
        assert len(body["tools_snapshot"]) == 1
        assert body["tools_snapshot"][0]["name"] == "search"
        mcp_server_id = body["id"]

        # list
        listed = await client.get(f"/api/v1/organizations/{org_id}/mcp-servers", headers=headers)
        assert listed.status_code == 200
        assert len(listed.json()) == 1

        # refresh — return a different snapshot
        fake_client.next_tools = [
            McpToolSnapshot(name="search", description="Search", input_schema={}),
            McpToolSnapshot(name="create_page", description="Create", input_schema={}),
        ]
        refresh = await client.post(
            f"/api/v1/organizations/{org_id}/mcp-servers/{mcp_server_id}/refresh",
            headers=headers,
        )
        assert refresh.status_code == 200
        assert len(refresh.json()["tools_snapshot"]) == 2

        # update — change name + URL + timeout (no auth change)
        update = await client.patch(
            f"/api/v1/organizations/{org_id}/mcp-servers/{mcp_server_id}",
            json={
                "name": "Notion Prod",
                "url": "https://mcp.notion-prod.test/",
                "timeout_seconds": 45,
                "auth_type": None,
                "bearer_token": None,
            },
            headers=headers,
        )
        assert update.status_code == 200
        assert update.json()["name"] == "Notion Prod"
        assert update.json()["timeout_seconds"] == 45
        # bearer token preserved
        assert update.json()["masked_token"] == "...wxyz"

        # deactivate then re-activate
        deactivate = await client.patch(
            f"/api/v1/organizations/{org_id}/mcp-servers/{mcp_server_id}/deactivate",
            headers=headers,
        )
        assert deactivate.status_code == 204
        after = (await client.get(f"/api/v1/organizations/{org_id}/mcp-servers", headers=headers)).json()
        assert after[0]["is_active"] is False

        activate = await client.patch(
            f"/api/v1/organizations/{org_id}/mcp-servers/{mcp_server_id}/activate",
            headers=headers,
        )
        assert activate.status_code == 204

        # delete
        delete = await client.delete(
            f"/api/v1/organizations/{org_id}/mcp-servers/{mcp_server_id}", headers=headers
        )
        assert delete.status_code == 204
        after_delete = await client.get(f"/api/v1/organizations/{org_id}/mcp-servers", headers=headers)
        assert after_delete.json() == []

    async def test_declare_returns_422_when_url_is_forbidden(
        self,
        client: AsyncClient,
        fake_mcp_services: tuple[_FakeUrlSafetyValidator, _FakeMcpClient],
    ) -> None:
        # Given
        validator, _ = fake_mcp_services
        validator.reject_urls.add("https://forbidden.test/")
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)

        # When
        response = await client.post(
            f"/api/v1/organizations/{org_id}/mcp-servers",
            json={
                "name": "Bad",
                "url": "https://forbidden.test/",
                "auth_type": "none",
                "bearer_token": None,
                "timeout_seconds": 30,
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 422

    async def test_endpoints_require_owner_or_maker_membership(
        self,
        client: AsyncClient,
        fake_mcp_services: tuple[_FakeUrlSafetyValidator, _FakeMcpClient],
    ) -> None:
        # Given
        owner_headers = await self._auth_headers(client)
        org_id = await self._create_org(client, owner_headers)
        outsider_headers = await self._auth_headers(client)

        # When — non-member tries to declare
        response = await client.post(
            f"/api/v1/organizations/{org_id}/mcp-servers",
            json={
                "name": "Notion",
                "url": "https://mcp.notion.test/",
                "auth_type": "none",
                "bearer_token": None,
                "timeout_seconds": 30,
            },
            headers=outsider_headers,
        )

        # Then
        assert response.status_code == 403

    async def test_update_returns_404_for_missing_server(
        self,
        client: AsyncClient,
        fake_mcp_services: tuple[_FakeUrlSafetyValidator, _FakeMcpClient],
    ) -> None:
        # Given
        headers = await self._auth_headers(client)
        org_id = await self._create_org(client, headers)
        missing_id = uuid4()

        # When
        response = await client.patch(
            f"/api/v1/organizations/{org_id}/mcp-servers/{missing_id}",
            json={
                "name": "Whatever",
                "url": "https://mcp.notion.test/",
                "timeout_seconds": 30,
                "auth_type": None,
                "bearer_token": None,
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 404
