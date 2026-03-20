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

    async def _create_organization(self, client: AsyncClient, headers: dict[str, str]) -> str:
        create = await client.post(
            "/api/v1/organizations",
            json={"name": "Acme Org", "description": "desc"},
            headers=headers,
        )
        assert create.status_code == 201
        return create.json()["id"]

    async def _auth_headers_with_email(
        self,
        client: AsyncClient,
    ) -> tuple[dict[str, str], str]:
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
        return {"Authorization": f"Bearer {token}"}, email

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

    async def test_organization_projects_listing(self, client: AsyncClient) -> None:
        headers = await self._auth_headers(client)
        organization_id = await self._create_organization(client, headers)

        create_project = await client.post(
            "/api/v1/projects",
            json={
                "name": "Org Project",
                "description": "attached",
                "organization_id": organization_id,
            },
            headers=headers,
        )
        assert create_project.status_code == 201
        assert create_project.json()["organization_id"] == organization_id

        projects = await client.get(
            f"/api/v1/organizations/{organization_id}/projects",
            headers=headers,
        )
        assert projects.status_code == 200
        assert len(projects.json()) == 1
        assert projects.json()[0]["name"] == "Org Project"

    async def test_organization_projects_forbidden_for_non_member(self, client: AsyncClient) -> None:
        owner_headers = await self._auth_headers(client)
        organization_id = await self._create_organization(client, owner_headers)
        other_headers = await self._auth_headers(client)

        listing = await client.get(
            f"/api/v1/organizations/{organization_id}/projects",
            headers=other_headers,
        )
        assert listing.status_code == 403

        create_project = await client.post(
            "/api/v1/projects",
            json={
                "name": "Forbidden Org Project",
                "description": "attached",
                "organization_id": organization_id,
            },
            headers=other_headers,
        )
        assert create_project.status_code == 403

    async def test_user_can_list_and_accept_pending_invitations(self, client: AsyncClient) -> None:
        owner_headers = await self._auth_headers(client)
        invitee_headers, invitee_email = await self._auth_headers_with_email(client)
        organization_id = await self._create_organization(client, owner_headers)

        invite = await client.post(
            f"/api/v1/organizations/{organization_id}/invitations",
            json={"email": invitee_email, "role": "maker"},
            headers=owner_headers,
        )
        assert invite.status_code == 200
        invitation_id = invite.json()["id"]

        pending = await client.get(
            "/api/v1/organizations/invitations/pending",
            headers=invitee_headers,
        )
        assert pending.status_code == 200
        assert len(pending.json()) == 1
        assert pending.json()[0]["id"] == invitation_id

        accepted = await client.post(
            f"/api/v1/organizations/invitations/{invitation_id}/accept",
            headers=invitee_headers,
        )
        assert accepted.status_code == 200
        assert accepted.json()["organization_id"] == organization_id

        members = await client.get(
            f"/api/v1/organizations/{organization_id}/members",
            headers=owner_headers,
        )
        assert members.status_code == 200
        assert len(members.json()) == 2

        invitee_organizations = await client.get(
            "/api/v1/organizations",
            headers=invitee_headers,
        )
        assert invitee_organizations.status_code == 200
        assert any(org["id"] == organization_id for org in invitee_organizations.json())

        invitee_settings = await client.get(
            f"/api/v1/organizations/{organization_id}",
            headers=invitee_headers,
        )
        assert invitee_settings.status_code == 403
