"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  deleteOrganization,
  getOrganization,
  updateOrganization,
} from "@/lib/api/organizations";
import type { UpdateOrganizationRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useOrganization(organizationId: string) {
  const { token } = useAuth();
  return useQuery({
    queryKey: ["organization", organizationId],
    queryFn: () => getOrganization(token!, organizationId),
    enabled: !!token && !!organizationId,
  });
}

export function useUpdateOrganization(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UpdateOrganizationRequest) =>
      updateOrganization(token!, organizationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization", organizationId] });
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
}

export function useDeleteOrganization(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => deleteOrganization(token!, organizationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
}
