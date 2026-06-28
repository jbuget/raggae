from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot


def test_mcp_tool_snapshot_holds_metadata() -> None:
    # Given / When
    snapshot = McpToolSnapshot(
        name="search",
        description="Search documents",
        input_schema={"type": "object", "properties": {"q": {"type": "string"}}},
    )

    # Then
    assert snapshot.name == "search"
    assert snapshot.description == "Search documents"
    assert snapshot.input_schema["type"] == "object"


def test_mcp_tool_snapshot_is_immutable() -> None:
    # Given
    snapshot = McpToolSnapshot(name="search", description="", input_schema={})

    # When / Then
    try:
        snapshot.name = "other"  # type: ignore[misc]
    except Exception:  # noqa: BLE001
        return
    raise AssertionError("McpToolSnapshot should be immutable")
