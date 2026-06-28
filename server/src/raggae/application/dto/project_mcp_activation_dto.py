from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ProjectMcpActivationDTO:
    project_id: UUID
    org_mcp_server_id: UUID
    is_active: bool
    activated_at: datetime
