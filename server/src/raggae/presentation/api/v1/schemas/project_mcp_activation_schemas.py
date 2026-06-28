from pydantic import BaseModel

from raggae.presentation.api.v1.schemas.org_mcp_server_schemas import OrgMcpServerResponse


class ProjectMcpActivationViewResponse(BaseModel):
    org_mcp_server: OrgMcpServerResponse
    is_activated: bool
