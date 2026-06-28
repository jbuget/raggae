from raggae.domain.value_objects.mcp_auth_type import McpAuthType


def test_mcp_auth_type_values() -> None:
    assert McpAuthType.NONE.value == "none"
    assert McpAuthType.BEARER.value == "bearer"


def test_mcp_auth_type_from_string() -> None:
    assert McpAuthType("none") is McpAuthType.NONE
    assert McpAuthType("bearer") is McpAuthType.BEARER
