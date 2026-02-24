from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.exceptions.organization_exceptions import LastOrganizationOwnerError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class TestOrganization:
    def test_update_profile_returns_updated_copy(self) -> None:
        now = datetime.now(UTC)
        organization = Organization(
            id=uuid4(),
            name="Raggae",
            slug=None,
            description="desc",
            logo_url=None,
            created_by_user_id=uuid4(),
            created_at=now,
            updated_at=now,
        )

        updated = organization.update_profile(
            name="Raggae AI",
            slug="raggae-ai",
            description="new desc",
            logo_url="https://example.com/logo.png",
            updated_at=now,
        )

        assert updated.name == "Raggae AI"
        assert updated.slug == "raggae-ai"
        assert updated.description == "new desc"
        assert updated.logo_url == "https://example.com/logo.png"
        assert organization.name == "Raggae"

    def test_organization_is_immutable(self) -> None:
        organization = Organization(
            id=uuid4(),
            name="Raggae",
            slug=None,
            description=None,
            logo_url=None,
            created_by_user_id=uuid4(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        with pytest.raises(FrozenInstanceError):
            organization.name = "Other"  # type: ignore[misc]

    def test_count_owners(self) -> None:
        organization_id = uuid4()
        members = [
            OrganizationMember(
                id=uuid4(),
                organization_id=organization_id,
                user_id=uuid4(),
                role=OrganizationMemberRole.OWNER,
                joined_at=datetime.now(UTC),
            ),
            OrganizationMember(
                id=uuid4(),
                organization_id=organization_id,
                user_id=uuid4(),
                role=OrganizationMemberRole.MAKER,
                joined_at=datetime.now(UTC),
            ),
        ]

        assert Organization.count_owners(members) == 1

    def test_cannot_remove_last_owner(self) -> None:
        organization_id = uuid4()
        owner = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=uuid4(),
            role=OrganizationMemberRole.OWNER,
            joined_at=datetime.now(UTC),
        )

        with pytest.raises(LastOrganizationOwnerError):
            Organization.ensure_can_remove_member(owner, [owner])

    def test_can_remove_owner_when_another_owner_exists(self) -> None:
        organization_id = uuid4()
        owner_a = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=uuid4(),
            role=OrganizationMemberRole.OWNER,
            joined_at=datetime.now(UTC),
        )
        owner_b = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=uuid4(),
            role=OrganizationMemberRole.OWNER,
            joined_at=datetime.now(UTC),
        )

        Organization.ensure_can_remove_member(owner_a, [owner_a, owner_b])

    def test_cannot_demote_last_owner(self) -> None:
        organization_id = uuid4()
        owner = OrganizationMember(
            id=uuid4(),
            organization_id=organization_id,
            user_id=uuid4(),
            role=OrganizationMemberRole.OWNER,
            joined_at=datetime.now(UTC),
        )

        with pytest.raises(LastOrganizationOwnerError):
            Organization.ensure_can_change_role(
                target_member=owner,
                next_role=OrganizationMemberRole.MAKER,
                members=[owner],
            )
