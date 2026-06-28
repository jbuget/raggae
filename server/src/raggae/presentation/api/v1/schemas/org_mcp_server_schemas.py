from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

_MIN_TIMEOUT_SECONDS = 5
_MAX_TIMEOUT_SECONDS = 60


class McpToolSnapshotResponse(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


class OrgMcpServerResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    url: str
    auth_type: str
    masked_token: str | None
    is_active: bool
    tools_snapshot: list[McpToolSnapshotResponse]
    tools_snapshot_at: datetime
    timeout_seconds: int
    created_at: datetime
    updated_at: datetime


class DeclareOrgMcpServerRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    url: str = Field(min_length=8, max_length=2048)
    auth_type: str = Field(default="none")
    bearer_token: str | None = Field(default=None, max_length=512)
    timeout_seconds: int = Field(default=30, ge=_MIN_TIMEOUT_SECONDS, le=_MAX_TIMEOUT_SECONDS)


class UpdateOrgMcpServerRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    url: str = Field(min_length=8, max_length=2048)
    timeout_seconds: int = Field(ge=_MIN_TIMEOUT_SECONDS, le=_MAX_TIMEOUT_SECONDS)
    auth_type: str | None = Field(default=None)
    bearer_token: str | None = Field(default=None, max_length=512)
