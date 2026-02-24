from datetime import UTC, datetime
import random
from uuid import UUID, uuid4

from raggae.application.dto.organization_dto import OrganizationDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class CreateOrganization:
    """Use Case: Create organization and bootstrap first owner."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository

    async def execute(
        self,
        user_id: UUID,
        name: str,
        slug: str | None = None,
        description: str | None = None,
        logo_url: str | None = None,
    ) -> OrganizationDTO:
        resolved_slug = slug.strip() if slug is not None and slug.strip() != "" else None
        if resolved_slug is None:
            resolved_slug = await self._generate_unique_slug()
        now = datetime.now(UTC)
        organization = Organization(
            id=uuid4(),
            name=name,
            slug=resolved_slug,
            description=description,
            logo_url=logo_url,
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        first_owner = OrganizationMember(
            id=uuid4(),
            organization_id=organization.id,
            user_id=user_id,
            role=OrganizationMemberRole.OWNER,
            joined_at=now,
        )
        await self._organization_repository.save(organization)
        await self._organization_member_repository.save(first_owner)
        return OrganizationDTO.from_entity(organization)

    async def _generate_unique_slug(self) -> str:
        adjectives = [
            "agile",
            "brave",
            "calme",
            "clair",
            "doux",
            "fiable",
            "fort",
            "futé",
            "grand",
            "juste",
            "libre",
            "loyal",
            "neuf",
            "rapide",
            "sage",
            "solide",
            "vif",
            "zen",
        ]
        nouns = [
            "atelier",
            "bastion",
            "canal",
            "citron",
            "delta",
            "faucon",
            "fjord",
            "garage",
            "horizon",
            "jardin",
            "lagon",
            "lierre",
            "marais",
            "nuage",
            "orchid",
            "phare",
            "rivage",
            "sillage",
        ]
        for _ in range(50):
            candidate = f"{random.choice(adjectives)}-{random.choice(nouns)}"
            existing = await self._organization_repository.find_by_slug(candidate)
            if existing is None:
                return candidate
        raise RuntimeError("Failed to generate a unique organization slug")
