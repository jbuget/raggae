from uuid import uuid4

from httpx import AsyncClient


class TestOrganizationEndpoints:
    async def _auth_headers(self, client: AsyncClient) -> dict[str, str]:
        unique = uuid4().hex
        email = f"{unique}@example.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "full_name": "Org User",
            },
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass123!"},
        )
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    async def test_organization_crud_and_members_flow(self, client: AsyncClient) -> None:
        headers = await self._auth_headers(client)

        create = await client.post(
            "/api/v1/organizations",
            json={"name": "Acme Org", "description": "desc"},
            headers=headers,
        )
        assert create.status_code == 201
        organization_id = create.json()["id"]

        listed = await client.get("/api/v1/organizations", headers=headers)
        assert listed.status_code == 200
        assert len(listed.json()) == 1

        detail = await client.get(f"/api/v1/organizations/{organization_id}", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["name"] == "Acme Org"

        updated = await client.patch(
            f"/api/v1/organizations/{organization_id}",
            json={"name": "Acme Updated", "description": "new", "logo_url": None},
            headers=headers,
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "Acme Updated"

        members = await client.get(
            f"/api/v1/organizations/{organization_id}/members",
            headers=headers,
        )
        assert members.status_code == 200
        assert len(members.json()) == 1
        assert members.json()[0]["role"] == "owner"

        invite = await client.post(
            f"/api/v1/organizations/{organization_id}/invitations",
            json={"email": "invitee@example.com", "role": "maker"},
            headers=headers,
        )
        assert invite.status_code == 200

        invitations = await client.get(
            f"/api/v1/organizations/{organization_id}/invitations",
            headers=headers,
        )
        assert invitations.status_code == 200
        assert len(invitations.json()) == 1
