"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  activateProjectMcp,
  deactivateProjectMcp,
  listProjectMcpActivations,
} from "@/lib/api/project-mcp-activations";
import { useAuth } from "./use-auth";

const queryKey = (projectId: string | null | undefined) =>
  ["project-mcp-activations", projectId] as const;

export function useProjectMcpActivations(projectId: string | null | undefined) {
  const { token } = useAuth();

  return useQuery({
    queryKey: queryKey(projectId),
    queryFn: () => listProjectMcpActivations(token!, projectId!),
    enabled: !!token && !!projectId,
  });
}

export function useActivateProjectMcp(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (mcpServerId: string) =>
      activateProjectMcp(token!, projectId, mcpServerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey(projectId) });
    },
  });
}

export function useDeactivateProjectMcp(projectId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (mcpServerId: string) =>
      deactivateProjectMcp(token!, projectId, mcpServerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey(projectId) });
    },
  });
}
