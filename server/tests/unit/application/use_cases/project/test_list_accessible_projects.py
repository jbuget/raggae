from datetime import UTC, datetime
from uuid import uuid4

from raggae.application.use_cases.project.list_accessible_projects import ListAccessibleProjects
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_organization_member_repository import (
    InMemoryOrganizationMemberRepository,
)
from raggae.infrastructure.database.repositories.in_memory_organization_repository import (
    InMemoryOrganizationRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)


def _org(org_id, name: str = "Org") -> Organization:
    now = datetime.now(UTC)
    return Organization(
        id=org_id,
        name=name,
        slug=None,
        description=None,
        logo_url=None,
        created_by_user_id=uuid4(),
        created_at=now,
        updated_at=now,
    )


def _membership(user_id, org_id, role: OrganizationMemberRole) -> OrganizationMember:
    return OrganizationMember(
        id=uuid4(),
        organization_id=org_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.now(UTC),
    )


def _project(name: str, user_id=None, organization_id=None, is_published: bool = False) -> Project:
    return Project(
        id=uuid4(),
        user_id=user_id or uuid4(),
        organization_id=organization_id,
        name=name,
        description="",
        system_prompt="",
        is_published=is_published,
        created_at=datetime.now(UTC),
    )


def _use_case(member_repo, org_repo, project_repo) -> ListAccessibleProjects:
    return ListAccessibleProjects(
        organization_member_repository=member_repo,
        organization_repository=org_repo,
        project_repository=project_repo,
    )


class TestListAccessibleProjects:
    async def test_returns_personal_projects(self) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        org_repo = InMemoryOrganizationRepository()
        project_repo = InMemoryProjectRepository()
        user_id = uuid4()
        await project_repo.save(_project("Personal", user_id=user_id))

        # When
        result = await _use_case(member_repo, org_repo, project_repo).execute(user_id=user_id)

        # Then
        assert len(result.personal_projects) == 1
        assert result.personal_projects[0].name == "Personal"
        assert result.organization_sections == []

    async def test_owner_sees_all_org_projects(self) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        org_repo = InMemoryOrganizationRepository()
        project_repo = InMemoryProjectRepository()
        user_id, org_id = uuid4(), uuid4()
        await org_repo.save(_org(org_id, "Acme"))
        await member_repo.save(_membership(user_id, org_id, OrganizationMemberRole.OWNER))
        await project_repo.save(_project("Published", organization_id=org_id, is_published=True))
        await project_repo.save(_project("Unpublished", organization_id=org_id, is_published=False))

        # When
        result = await _use_case(member_repo, org_repo, project_repo).execute(user_id=user_id)

        # Then
        assert len(result.organization_sections) == 1
        section = result.organization_sections[0]
        assert section.organization_name == "Acme"
        assert section.can_edit is True
        assert len(section.projects) == 2

    async def test_maker_sees_all_org_projects_with_can_edit(self) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        org_repo = InMemoryOrganizationRepository()
        project_repo = InMemoryProjectRepository()
        user_id, org_id = uuid4(), uuid4()
        await org_repo.save(_org(org_id))
        await member_repo.save(_membership(user_id, org_id, OrganizationMemberRole.MAKER))
        await project_repo.save(_project("Published", organization_id=org_id, is_published=True))
        await project_repo.save(_project("Unpublished", organization_id=org_id, is_published=False))

        # When
        result = await _use_case(member_repo, org_repo, project_repo).execute(user_id=user_id)

        # Then
        section = result.organization_sections[0]
        assert section.can_edit is True
        assert len(section.projects) == 2

    async def test_user_role_sees_only_published_org_projects(self) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        org_repo = InMemoryOrganizationRepository()
        project_repo = InMemoryProjectRepository()
        user_id, org_id = uuid4(), uuid4()
        await org_repo.save(_org(org_id))
        await member_repo.save(_membership(user_id, org_id, OrganizationMemberRole.USER))
        await project_repo.save(_project("Published", organization_id=org_id, is_published=True))
        await project_repo.save(_project("Unpublished", organization_id=org_id, is_published=False))

        # When
        result = await _use_case(member_repo, org_repo, project_repo).execute(user_id=user_id)

        # Then
        section = result.organization_sections[0]
        assert section.can_edit is False
        assert len(section.projects) == 1
        assert section.projects[0].name == "Published"

    async def test_aggregates_personal_and_org_projects(self) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        org_repo = InMemoryOrganizationRepository()
        project_repo = InMemoryProjectRepository()
        user_id, org_id = uuid4(), uuid4()
        await org_repo.save(_org(org_id, "Corp"))
        await member_repo.save(_membership(user_id, org_id, OrganizationMemberRole.OWNER))
        await project_repo.save(_project("Personal", user_id=user_id))
        await project_repo.save(_project("Org project", organization_id=org_id, is_published=True))

        # When
        result = await _use_case(member_repo, org_repo, project_repo).execute(user_id=user_id)

        # Then
        assert len(result.personal_projects) == 1
        assert result.personal_projects[0].name == "Personal"
        assert len(result.organization_sections) == 1
        assert result.organization_sections[0].projects[0].name == "Org project"

    async def test_returns_empty_for_user_with_no_projects(self) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        org_repo = InMemoryOrganizationRepository()
        project_repo = InMemoryProjectRepository()

        # When
        result = await _use_case(member_repo, org_repo, project_repo).execute(user_id=uuid4())

        # Then
        assert result.personal_projects == []
        assert result.organization_sections == []

    async def test_fetches_all_org_projects_without_n_plus_1(self) -> None:
        """Plusieurs orgs → une seule passe de récupération des projets."""
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        org_repo = InMemoryOrganizationRepository()
        project_repo = InMemoryProjectRepository()
        user_id = uuid4()
        org_a, org_b = uuid4(), uuid4()
        await org_repo.save(_org(org_a, "Alpha"))
        await org_repo.save(_org(org_b, "Beta"))
        await member_repo.save(_membership(user_id, org_a, OrganizationMemberRole.OWNER))
        await member_repo.save(_membership(user_id, org_b, OrganizationMemberRole.OWNER))
        await project_repo.save(_project("A1", organization_id=org_a))
        await project_repo.save(_project("A2", organization_id=org_a))
        await project_repo.save(_project("B1", organization_id=org_b))

        # When
        result = await _use_case(member_repo, org_repo, project_repo).execute(user_id=user_id)

        # Then
        assert len(result.organization_sections) == 2
        alpha = next(s for s in result.organization_sections if s.organization_name == "Alpha")
        beta = next(s for s in result.organization_sections if s.organization_name == "Beta")
        assert {p.name for p in alpha.projects} == {"A1", "A2"}
        assert {p.name for p in beta.projects} == {"B1"}
