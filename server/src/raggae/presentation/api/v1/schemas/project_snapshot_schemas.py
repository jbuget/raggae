from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectSnapshotResponse(BaseModel):
    id: UUID
    project_id: UUID
    version_number: int
    label: str | None
    created_at: datetime
    created_by_user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    organization_id: UUID | None
    restored_from_version: int | None


class ProjectSnapshotListResponse(BaseModel):
    snapshots: list[ProjectSnapshotResponse]
    total: int
    limit: int
    offset: int
