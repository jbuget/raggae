from datetime import UTC, datetime
from uuid import uuid4

from raggae.application.use_cases.project.list_accessible_projects import ListAccessibleProjects
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_organization_member_repository import (
    InMemoryOrganizationMemberRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)


class TestListAccessibleProjects:
    async def test_list_accessible_projects_returns_personal_projects(self) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListAccessibleProjects(
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )
        now = datetime.now(UTC)
        user_id = uuid4()
        personal_project = Project(
            id=uuid4(),
            user_id=user_id,
            organization_id=None,
            name="Personal project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=now,
        )
        await project_repo.save(personal_project)

        # When
        result = await use_case.execute(user_id=user_id)

        # Then
        assert len(result) == 1
        assert result[0].name == "Personal project"

    async def test_list_accessible_projects_includes_org_projects_for_owner(self) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListAccessibleProjects(
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )
        now = datetime.now(UTC)
        user_id = uuid4()
        org_id = uuid4()
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=org_id,
                user_id=user_id,
                role=OrganizationMemberRole.OWNER,
                joined_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=uuid4(),
                organization_id=org_id,
                name="Org published",
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
                organization_id=org_id,
                name="Org unpublished",
                description="",
                system_prompt="",
                is_published=False,
                created_at=now,
            )
        )

        # When
        result = await use_case.execute(user_id=user_id)

        # Then owner sees all org projects (published and unpublished)
        assert len(result) == 2

    async def test_list_accessible_projects_includes_org_projects_for_maker(self) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListAccessibleProjects(
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )
        now = datetime.now(UTC)
        user_id = uuid4()
        org_id = uuid4()
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=org_id,
                user_id=user_id,
                role=OrganizationMemberRole.MAKER,
                joined_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=uuid4(),
                organization_id=org_id,
                name="Org published",
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
                organization_id=org_id,
                name="Org unpublished",
                description="",
                system_prompt="",
                is_published=False,
                created_at=now,
            )
        )

        # When
        result = await use_case.execute(user_id=user_id)

        # Then maker sees all org projects (published and unpublished)
        assert len(result) == 2

    async def test_list_accessible_projects_user_role_sees_only_published_org_projects(
        self,
    ) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListAccessibleProjects(
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )
        now = datetime.now(UTC)
        user_id = uuid4()
        org_id = uuid4()
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=org_id,
                user_id=user_id,
                role=OrganizationMemberRole.USER,
                joined_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=uuid4(),
                organization_id=org_id,
                name="Published",
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
                organization_id=org_id,
                name="Unpublished",
                description="",
                system_prompt="",
                is_published=False,
                created_at=now,
            )
        )

        # When
        result = await use_case.execute(user_id=user_id)

        # Then USER role member sees only published projects
        assert len(result) == 1
        assert result[0].name == "Published"

    async def test_list_accessible_projects_aggregates_personal_and_org_projects(
        self,
    ) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListAccessibleProjects(
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )
        now = datetime.now(UTC)
        user_id = uuid4()
        org_id = uuid4()
        await member_repo.save(
            OrganizationMember(
                id=uuid4(),
                organization_id=org_id,
                user_id=user_id,
                role=OrganizationMemberRole.OWNER,
                joined_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=user_id,
                organization_id=None,
                name="Personal",
                description="",
                system_prompt="",
                is_published=False,
                created_at=now,
            )
        )
        await project_repo.save(
            Project(
                id=uuid4(),
                user_id=uuid4(),
                organization_id=org_id,
                name="Org project",
                description="",
                system_prompt="",
                is_published=True,
                created_at=now,
            )
        )

        # When
        result = await use_case.execute(user_id=user_id)

        # Then both personal and org projects are returned
        assert len(result) == 2
        names = {p.name for p in result}
        assert names == {"Personal", "Org project"}

    async def test_list_accessible_projects_returns_empty_for_user_with_no_projects(
        self,
    ) -> None:
        # Given
        member_repo = InMemoryOrganizationMemberRepository()
        project_repo = InMemoryProjectRepository()
        use_case = ListAccessibleProjects(
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )

        # When
        result = await use_case.execute(user_id=uuid4())

        # Then
        assert result == []
