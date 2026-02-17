import type {
  CreateProjectRequest,
  ProjectResponse,
  ReindexProjectResponse,
  UpdateProjectRequest,
} from "@/lib/types/api";
import { apiFetch } from "./client";

export function listProjects(token: string): Promise<ProjectResponse[]> {
  return apiFetch<ProjectResponse[]>("/projects", { token });
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
