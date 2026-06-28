from raggae.domain.value_objects.mcp_slug import slugify


def test_slugify_simple_name() -> None:
    assert slugify("My MCP") == "my-mcp"


def test_slugify_strips_special_chars() -> None:
    assert slugify("Acme/Notion (prod)") == "acme-notion-prod"


def test_slugify_collapses_separators() -> None:
    assert slugify("foo   bar---baz") == "foo-bar-baz"


def test_slugify_trims_dashes() -> None:
    assert slugify("---hello---") == "hello"


def test_slugify_drops_diacritics_replaced_by_dash() -> None:
    # Non-ASCII chars become separators (kebab-case ASCII)
    assert slugify("résumé") == "r-sum"


def test_slugify_empty_falls_back_to_default() -> None:
    assert slugify("   ") == "mcp"
    assert slugify("!!!") == "mcp"
