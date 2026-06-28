import { apiFetch } from "@/lib/api/client";
import type {
  DeclareOrgMcpServerRequest,
  OrgMcpServerResponse,
  UpdateOrgMcpServerRequest,
} from "@/lib/types/api";

export function listOrgMcpServers(
  token: string,
  organizationId: string,
): Promise<OrgMcpServerResponse[]> {
  return apiFetch<OrgMcpServerResponse[]>(
    `/organizations/${organizationId}/mcp-servers`,
    { token },
  );
}

export function declareOrgMcpServer(
  token: string,
  organizationId: string,
  data: DeclareOrgMcpServerRequest,
): Promise<OrgMcpServerResponse> {
  return apiFetch<OrgMcpServerResponse>(
    `/organizations/${organizationId}/mcp-servers`,
    { method: "POST", token, body: JSON.stringify(data) },
  );
}

export function updateOrgMcpServer(
  token: string,
  organizationId: string,
  mcpServerId: string,
  data: UpdateOrgMcpServerRequest,
): Promise<OrgMcpServerResponse> {
  return apiFetch<OrgMcpServerResponse>(
    `/organizations/${organizationId}/mcp-servers/${mcpServerId}`,
    { method: "PATCH", token, body: JSON.stringify(data) },
  );
}

export function refreshOrgMcpTools(
  token: string,
  organizationId: string,
  mcpServerId: string,
): Promise<OrgMcpServerResponse> {
  return apiFetch<OrgMcpServerResponse>(
    `/organizations/${organizationId}/mcp-servers/${mcpServerId}/refresh`,
    { method: "POST", token },
  );
}

export function activateOrgMcpServer(
  token: string,
  organizationId: string,
  mcpServerId: string,
): Promise<void> {
  return apiFetch<void>(
    `/organizations/${organizationId}/mcp-servers/${mcpServerId}/activate`,
    { method: "PATCH", token },
  );
}

export function deactivateOrgMcpServer(
  token: string,
  organizationId: string,
  mcpServerId: string,
): Promise<void> {
  return apiFetch<void>(
    `/organizations/${organizationId}/mcp-servers/${mcpServerId}/deactivate`,
    { method: "PATCH", token },
  );
}

export function deleteOrgMcpServer(
  token: string,
  organizationId: string,
  mcpServerId: string,
): Promise<void> {
  return apiFetch<void>(
    `/organizations/${organizationId}/mcp-servers/${mcpServerId}`,
    { method: "DELETE", token },
  );
}
