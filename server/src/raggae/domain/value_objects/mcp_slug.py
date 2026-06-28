import re

_NON_KEBAB = re.compile(r"[^a-z0-9]+")
_MULTI_DASH = re.compile(r"-+")


def slugify(name: str) -> str:
    """Build a kebab-case ASCII slug from a human-friendly name.

    Falls back to `'mcp'` when no kebab characters remain.
    """
    lowered = name.lower()
    replaced = _NON_KEBAB.sub("-", lowered)
    collapsed = _MULTI_DASH.sub("-", replaced).strip("-")
    return collapsed or "mcp"
