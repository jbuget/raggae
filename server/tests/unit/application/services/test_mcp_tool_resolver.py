from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

from raggae.application.services.mcp_tool_resolver import McpToolResolver
from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.entities.project import Project
from raggae.domain.entities.project_mcp_activation import ProjectMcpActivation
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot


def _make_project(*, project_id: UUID | None = None, organization_id: UUID | None = None) -> Project:
    return Project(
        id=project_id or uuid4(),
        user_id=uuid4(),
        name="P",
        description="",
        system_prompt="",
        is_published=False,
        created_at=datetime.now(UTC),
        organization_id=organization_id,
    )


def _make_server(
    *,
    organization_id: UUID,
    slug: str,
    tools: list[McpToolSnapshot] | None = None,
    is_active: bool = True,
    auth_type: McpAuthType = McpAuthType.NONE,
) -> OrgMcpServer:
    now = datetime.now(UTC)
    return OrgMcpServer(
        id=uuid4(),
        organization_id=organization_id,
        name=slug.capitalize(),
        slug=slug,
        url=f"https://mcp.{slug}.test/",
        auth_type=auth_type,
        encrypted_bearer_token="enc" if auth_type == McpAuthType.BEARER else None,
        token_fingerprint="fp" if auth_type == McpAuthType.BEARER else None,
        token_suffix="abcd" if auth_type == McpAuthType.BEARER else None,
        is_active=is_active,
        tools_snapshot=tools or [],
        tools_snapshot_at=now,
        timeout_seconds=42,
        created_at=now,
        updated_at=now,
        created_by_user_id=uuid4(),
    )


def _make_activation(*, project_id: UUID, server_id: UUID, is_active: bool = True) -> ProjectMcpActivation:
    return ProjectMcpActivation(
        project_id=project_id,
        org_mcp_server_id=server_id,
        is_active=is_active,
        activated_at=datetime.now(UTC),
        activated_by_user_id=uuid4(),
    )


def _build_resolver(
    *,
    project: Project | None,
    servers: list[OrgMcpServer] | None = None,
    activations: list[ProjectMcpActivation] | None = None,
) -> McpToolResolver:
    servers_by_id = {s.id: s for s in (servers or [])}
    project_repo = AsyncMock()
    project_repo.find_by_id = AsyncMock(return_value=project)
    server_repo = AsyncMock()

    async def _find_by_id(server_id: UUID, _org_id: UUID) -> object | None:
        return servers_by_id.get(server_id)

    server_repo.find_by_id = AsyncMock(side_effect=_find_by_id)
    activation_repo = AsyncMock()
    activation_repo.list_by_project_id = AsyncMock(return_value=activations or [])
    return McpToolResolver(
        project_repository=project_repo,
        org_mcp_server_repository=server_repo,
        project_mcp_activation_repository=activation_repo,
    )


class TestMcpToolResolver:
    async def test_returns_prefixed_tools_from_active_activations(self) -> None:
        # Given
        org_id = uuid4()
        project = _make_project(organization_id=org_id)
        server = _make_server(
            organization_id=org_id,
            slug="notion",
            tools=[
                McpToolSnapshot(name="search", description="Search", input_schema={"q": "str"}),
                McpToolSnapshot(name="create_page", description="Create", input_schema={}),
            ],
        )
        activation = _make_activation(project_id=project.id, server_id=server.id)
        resolver = _build_resolver(project=project, servers=[server], activations=[activation])

        # When
        descriptors = await resolver.resolve(project.id)

        # Then
        assert [d.prefixed_name for d in descriptors] == [
            "notion__search",
            "notion__create_page",
        ]
        assert descriptors[0].mcp_server_id == server.id
        assert descriptors[0].original_name == "search"
        assert descriptors[0].server_url == server.url
        assert descriptors[0].timeout_seconds == 42

    async def test_skips_inactive_activations(self) -> None:
        # Given
        org_id = uuid4()
        project = _make_project(organization_id=org_id)
        server = _make_server(
            organization_id=org_id,
            slug="notion",
            tools=[McpToolSnapshot(name="x", description="", input_schema={})],
        )
        inactive_activation = _make_activation(project_id=project.id, server_id=server.id, is_active=False)
        resolver = _build_resolver(project=project, servers=[server], activations=[inactive_activation])

        # When
        descriptors = await resolver.resolve(project.id)

        # Then
        assert descriptors == []

    async def test_skips_servers_deactivated_at_org_level(self) -> None:
        # Given
        org_id = uuid4()
        project = _make_project(organization_id=org_id)
        server = _make_server(
            organization_id=org_id,
            slug="notion",
            tools=[McpToolSnapshot(name="x", description="", input_schema={})],
            is_active=False,
        )
        activation = _make_activation(project_id=project.id, server_id=server.id)
        resolver = _build_resolver(project=project, servers=[server], activations=[activation])

        # When
        descriptors = await resolver.resolve(project.id)

        # Then
        assert descriptors == []

    async def test_returns_empty_for_user_owned_project(self) -> None:
        # Given
        project = _make_project(organization_id=None)
        resolver = _build_resolver(project=project)

        # When / Then
        assert await resolver.resolve(project.id) == []

    async def test_returns_empty_when_project_does_not_exist(self) -> None:
        resolver = _build_resolver(project=None)
        assert await resolver.resolve(uuid4()) == []

    async def test_flags_bearer_token_when_present(self) -> None:
        # Given
        org_id = uuid4()
        project = _make_project(organization_id=org_id)
        server = _make_server(
            organization_id=org_id,
            slug="github",
            tools=[McpToolSnapshot(name="ping", description="", input_schema={})],
            auth_type=McpAuthType.BEARER,
        )
        activation = _make_activation(project_id=project.id, server_id=server.id)
        resolver = _build_resolver(project=project, servers=[server], activations=[activation])

        # When
        descriptors = await resolver.resolve(project.id)

        # Then
        assert descriptors[0].has_bearer_token is True

    async def test_aggregates_tools_across_multiple_servers(self) -> None:
        # Given
        org_id = uuid4()
        project = _make_project(organization_id=org_id)
        notion = _make_server(
            organization_id=org_id,
            slug="notion",
            tools=[McpToolSnapshot(name="search", description="", input_schema={})],
        )
        github = _make_server(
            organization_id=org_id,
            slug="github",
            tools=[McpToolSnapshot(name="search", description="", input_schema={})],
        )
        resolver = _build_resolver(
            project=project,
            servers=[notion, github],
            activations=[
                _make_activation(project_id=project.id, server_id=notion.id),
                _make_activation(project_id=project.id, server_id=github.id),
            ],
        )

        # When
        descriptors = await resolver.resolve(project.id)

        # Then — both `search` tools coexist thanks to the prefix
        prefixed = sorted(d.prefixed_name for d in descriptors)
        assert prefixed == ["github__search", "notion__search"]


class TestSplitPrefixedName:
    def test_splits_well_formed_name(self) -> None:
        assert McpToolResolver.split_prefixed_name("notion__search") == ("notion", "search")

    def test_returns_none_without_separator(self) -> None:
        assert McpToolResolver.split_prefixed_name("search") is None

    def test_returns_none_with_empty_parts(self) -> None:
        assert McpToolResolver.split_prefixed_name("__search") is None
        assert McpToolResolver.split_prefixed_name("notion__") is None
