from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class McpToolSnapshotDTO:
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class OrgMcpServerDTO:
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    url: str
    auth_type: str
    masked_token: str | None
    is_active: bool
    tools_snapshot_at: datetime
    timeout_seconds: int
    created_at: datetime
    updated_at: datetime
    tools_snapshot: list[McpToolSnapshotDTO] = field(default_factory=list)
