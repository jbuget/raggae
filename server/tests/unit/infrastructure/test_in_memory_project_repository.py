from datetime import UTC, datetime
from uuid import uuid4

from raggae.domain.entities.project import Project
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)


def _project(name: str, organization_id=None, user_id=None) -> Project:
    return Project(
        id=uuid4(),
        user_id=user_id or uuid4(),
        organization_id=organization_id,
        name=name,
        description="",
        system_prompt="",
        is_published=False,
        created_at=datetime.now(UTC),
    )


class TestInMemoryProjectRepositoryFindByOrganizationIds:
    async def test_returns_projects_for_matching_orgs(self) -> None:
        # Given
        repo = InMemoryProjectRepository()
        org_a, org_b, org_c = uuid4(), uuid4(), uuid4()
        await repo.save(_project("A", organization_id=org_a))
        await repo.save(_project("B", organization_id=org_b))
        await repo.save(_project("C", organization_id=org_c))

        # When
        result = await repo.find_by_organization_ids([org_a, org_b])

        # Then
        assert len(result) == 2
        assert {p.name for p in result} == {"A", "B"}

    async def test_returns_empty_when_no_org_matches(self) -> None:
        # Given
        repo = InMemoryProjectRepository()
        await repo.save(_project("X", organization_id=uuid4()))

        # When
        result = await repo.find_by_organization_ids([uuid4()])

        # Then
        assert result == []

    async def test_returns_empty_for_empty_ids_list(self) -> None:
        # Given
        repo = InMemoryProjectRepository()
        await repo.save(_project("X", organization_id=uuid4()))

        # When
        result = await repo.find_by_organization_ids([])

        # Then
        assert result == []

    async def test_returns_multiple_projects_per_org(self) -> None:
        # Given
        repo = InMemoryProjectRepository()
        org_id = uuid4()
        await repo.save(_project("P1", organization_id=org_id))
        await repo.save(_project("P2", organization_id=org_id))
        await repo.save(_project("P3", organization_id=uuid4()))

        # When
        result = await repo.find_by_organization_ids([org_id])

        # Then
        assert len(result) == 2
        assert {p.name for p in result} == {"P1", "P2"}
