from unittest.mock import AsyncMock

from raggae.application.use_cases.stats.get_mcp_stats import GetMcpStats


async def test_get_mcp_stats_aggregates_counts() -> None:
    # Given
    server_repo = AsyncMock()
    server_repo.count_all = AsyncMock(return_value=7)
    server_repo.count_active = AsyncMock(return_value=5)
    activation_repo = AsyncMock()
    activation_repo.count_active_activations = AsyncMock(return_value=11)
    activation_repo.count_distinct_active_projects = AsyncMock(return_value=4)
    use_case = GetMcpStats(
        org_mcp_server_repository=server_repo,
        project_mcp_activation_repository=activation_repo,
    )

    # When
    result = await use_case.execute()

    # Then
    assert result.org_servers_total == 7
    assert result.org_servers_active == 5
    assert result.project_activations_active == 11
    assert result.projects_with_at_least_one_activation == 4
