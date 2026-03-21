"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getProjectSnapshot,
  listProjectSnapshots,
  restoreProjectSnapshot,
} from "@/lib/api/project-snapshots";
import { useAuth } from "./use-auth";

export function useProjectSnapshots(
  projectId: string,
  limit = 20,
  offset = 0,
) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["projects", projectId, "snapshots"],
    queryFn: () => listProjectSnapshots(token!, projectId, limit, offset),
    enabled: !!token && !!projectId,
  });
}

export function useProjectSnapshot(projectId: string, versionNumber: number) {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["projects", projectId, "snapshots", versionNumber],
    queryFn: () => getProjectSnapshot(token!, projectId, versionNumber),
    enabled: !!token && !!projectId && versionNumber > 0,
  });
}

export function useRestoreProjectSnapshot(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (versionNumber: number) =>
      restoreProjectSnapshot(token!, projectId, versionNumber),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["projects", projectId, "snapshots"],
      });
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
    },
  });
}
