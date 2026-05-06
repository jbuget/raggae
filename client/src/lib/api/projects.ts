import type {
  AccessibleProjectsResponse,
  AgentConfigurationResponse,
  CreateProjectRequest,
  ProjectResponse,
  ReindexProjectResponse,
  UpdateAgentConfigurationRequest,
  UpdateProjectRequest,
} from "@/lib/types/api";
import { ApiError, apiFetch } from "./client";

export function listProjects(token: string): Promise<ProjectResponse[]> {
  return apiFetch<ProjectResponse[]>("/projects", { token });
}

export function listAccessibleProjects(token: string): Promise<AccessibleProjectsResponse> {
  return apiFetch<AccessibleProjectsResponse>("/projects/accessible", { token });
}

export function getProject(
  token: string,
  projectId: string,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/projects/${projectId}`, { token });
}

export function createProject(
  token: string,
  data: CreateProjectRequest,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>("/projects", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function updateProject(
  token: string,
  projectId: string,
  data: UpdateProjectRequest,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/projects/${projectId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
    token,
  });
}

export function deleteProject(
  token: string,
  projectId: string,
): Promise<void> {
  return apiFetch<void>(`/projects/${projectId}`, {
    method: "DELETE",
    token,
  });
}

export function reindexProject(
  token: string,
  projectId: string,
): Promise<ReindexProjectResponse> {
  return apiFetch<ReindexProjectResponse>(`/projects/${projectId}/reindex`, {
    method: "POST",
    token,
  });
}

export function publishProject(
  token: string,
  projectId: string,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/projects/${projectId}/publish`, {
    method: "POST",
    token,
  });
}

export function unpublishProject(
  token: string,
  projectId: string,
): Promise<ProjectResponse> {
  return apiFetch<ProjectResponse>(`/projects/${projectId}/unpublish`, {
    method: "POST",
    token,
  });
}

export async function getProjectConfiguration(
  token: string,
  projectId: string,
): Promise<AgentConfigurationResponse | null> {
  try {
    return await apiFetch<AgentConfigurationResponse>(`/projects/${projectId}/configuration`, { token });
  } catch (err: unknown) {
    if (err instanceof ApiError && err.status === 404) {
      return null;
    }
    throw err;
  }
}

export function updateProjectConfiguration(
  token: string,
  projectId: string,
  data: UpdateAgentConfigurationRequest,
): Promise<AgentConfigurationResponse> {
  return apiFetch<AgentConfigurationResponse>(`/projects/${projectId}/configuration`, {
    method: "PUT",
    body: JSON.stringify(data),
    token,
  });
}
