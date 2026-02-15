"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createProject,
  deleteProject,
  getProject,
  listProjects,
  updateProject,
} from "@/lib/api/projects";
import type { CreateProjectRequest, UpdateProjectRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useProjects() {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["projects"],
    queryFn: () => listProjects(token!),
    enabled: !!token,
  });
}

export function useProject(projectId: string) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["projects", projectId],
    queryFn: () => getProject(token!, projectId),
    enabled: !!token && !!projectId,
  });
}

export function useCreateProject() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProjectRequest) => createProject(token!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useUpdateProject(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProjectRequest) =>
      updateProject(token!, projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
    },
  });
}

export function useDeleteProject() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (projectId: string) => deleteProject(token!, projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
