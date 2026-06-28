import { apiFetch } from "@/lib/api/client";
import type { ProjectMcpActivationViewResponse } from "@/lib/types/api";

export function listProjectMcpActivations(
  token: string,
  projectId: string,
): Promise<ProjectMcpActivationViewResponse[]> {
  return apiFetch<ProjectMcpActivationViewResponse[]>(
    `/projects/${projectId}/mcp-activations`,
    { token },
  );
}

export function activateProjectMcp(
  token: string,
  projectId: string,
  mcpServerId: string,
): Promise<void> {
  return apiFetch<void>(
    `/projects/${projectId}/mcp-activations/${mcpServerId}`,
    { method: "POST", token },
  );
}

export function deactivateProjectMcp(
  token: string,
  projectId: string,
  mcpServerId: string,
): Promise<void> {
  return apiFetch<void>(
    `/projects/${projectId}/mcp-activations/${mcpServerId}`,
    { method: "DELETE", token },
  );
}
