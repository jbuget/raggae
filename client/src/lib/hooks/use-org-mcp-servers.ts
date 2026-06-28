"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  activateOrgMcpServer,
  deactivateOrgMcpServer,
  declareOrgMcpServer,
  deleteOrgMcpServer,
  listOrgMcpServers,
  refreshOrgMcpTools,
  updateOrgMcpServer,
} from "@/lib/api/org-mcp-servers";
import type {
  DeclareOrgMcpServerRequest,
  UpdateOrgMcpServerRequest,
} from "@/lib/types/api";
import { useAuth } from "./use-auth";

const queryKey = (organizationId: string | null | undefined) =>
  ["org-mcp-servers", organizationId] as const;

export function useOrgMcpServers(organizationId: string | null | undefined) {
  const { token } = useAuth();

  return useQuery({
    queryKey: queryKey(organizationId),
    queryFn: () => listOrgMcpServers(token!, organizationId!),
    enabled: !!token && !!organizationId,
  });
}

export function useDeclareOrgMcpServer(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DeclareOrgMcpServerRequest) =>
      declareOrgMcpServer(token!, organizationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey(organizationId) });
    },
  });
}

export function useUpdateOrgMcpServer(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      mcpServerId,
      data,
    }: {
      mcpServerId: string;
      data: UpdateOrgMcpServerRequest;
    }) => updateOrgMcpServer(token!, organizationId, mcpServerId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey(organizationId) });
    },
  });
}

export function useRefreshOrgMcpTools(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (mcpServerId: string) =>
      refreshOrgMcpTools(token!, organizationId, mcpServerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey(organizationId) });
    },
  });
}

export function useActivateOrgMcpServer(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (mcpServerId: string) =>
      activateOrgMcpServer(token!, organizationId, mcpServerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey(organizationId) });
    },
  });
}

export function useDeactivateOrgMcpServer(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (mcpServerId: string) =>
      deactivateOrgMcpServer(token!, organizationId, mcpServerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey(organizationId) });
    },
  });
}

export function useDeleteOrgMcpServer(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (mcpServerId: string) =>
      deleteOrgMcpServer(token!, organizationId, mcpServerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey(organizationId) });
    },
  });
}
