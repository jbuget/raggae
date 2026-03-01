from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.organization.list_organization_projects import (
    ListOrganizationProjects,
)
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
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


class TestListOrganizationProjects:
    async def test_list_projects_for_member_returns_projects(self) -> None:
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListOrganizationProjects(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )
        now = datetime.now(UTC)
        user_id = uuid4()
        organization = Organization(
            id=uuid4(),
            name="Acme",
            slug=None,
            description=None,
            logo_url=None,
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        await org_repo.save(organization)
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=organization.id,
                user_id=user_id,
                role=OrganizationMemberRole.OWNER,
                joined_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=user_id,
                organization_id=organization.id,
                name="Org project",
                description="desc",
                system_prompt="",
                is_published=False,
                created_at=now,
            )
        )

        projects = await use_case.execute(organization_id=organization.id, user_id=user_id)

        assert len(projects) == 1
        assert projects[0].organization_id == organization.id

    async def test_list_projects_user_role_returns_only_published(self) -> None:
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListOrganizationProjects(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )
        now = datetime.now(UTC)
        user_id = uuid4()
        organization = Organization(
            id=uuid4(),
            name="Acme",
            slug=None,
            description=None,
            logo_url=None,
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        await org_repo.save(organization)
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=organization.id,
                user_id=user_id,
                role=OrganizationMemberRole.USER,
                joined_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=uuid4(),
                organization_id=organization.id,
                name="Published project",
                description="",
                system_prompt="",
                is_published=True,
                created_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=uuid4(),
                organization_id=organization.id,
                name="Unpublished project",
                description="",
                system_prompt="",
                is_published=False,
                created_at=now,
            )
        )

        # Given a USER role member
        # When listing organization projects
        projects = await use_case.execute(organization_id=organization.id, user_id=user_id)

        # Then only published projects are returned
        assert len(projects) == 1
        assert projects[0].name == "Published project"

    async def test_list_projects_maker_role_returns_all_projects(self) -> None:
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListOrganizationProjects(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )
        now = datetime.now(UTC)
        user_id = uuid4()
        organization = Organization(
            id=uuid4(),
            name="Acme",
            slug=None,
            description=None,
            logo_url=None,
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        await org_repo.save(organization)
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=organization.id,
                user_id=user_id,
                role=OrganizationMemberRole.MAKER,
                joined_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=uuid4(),
                organization_id=organization.id,
                name="Published project",
                description="",
                system_prompt="",
                is_published=True,
                created_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=uuid4(),
                organization_id=organization.id,
                name="Unpublished project",
                description="",
                system_prompt="",
                is_published=False,
                created_at=now,
            )
        )

        # Given a MAKER role member
        # When listing organization projects
        projects = await use_case.execute(organization_id=organization.id, user_id=user_id)

        # Then all projects (published and unpublished) are returned
        assert len(projects) == 2

    async def test_list_projects_for_non_member_raises(self) -> None:
        org_repo = InMemoryOrganizationRepository()
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListOrganizationProjects(
            organization_repository=org_repo,
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )
        now = datetime.now(UTC)
        owner_id = uuid4()
        organization = Organization(
            id=uuid4(),
            name="Acme",
            slug=None,
            description=None,
            logo_url=None,
            created_by_user_id=owner_id,
            created_at=now,
            updated_at=now,
        )
        await org_repo.save(organization)

        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=organization.id, user_id=uuid4())

    async def test_list_projects_for_unknown_organization_raises(self) -> None:
        use_case = ListOrganizationProjects(
            organization_repository=InMemoryOrganizationRepository(),
            organization_member_repository=InMemoryOrganizationMemberRepository(),
            project_repository=InMemoryProjectRepository(),
        )

        with pytest.raises(OrganizationNotFoundError):
            await use_case.execute(organization_id=uuid4(), user_id=uuid4())
