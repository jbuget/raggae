"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createOrganization,
  listOrganizationProjects,
  listOrganizations,
} from "@/lib/api/organizations";
import type { CreateOrganizationRequest } from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useOrganizations() {
  const { token } = useAuth();
  return useQuery({
    queryKey: ["organizations"],
    queryFn: () => listOrganizations(token!),
    enabled: !!token,
  });
}

export function useCreateOrganization() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateOrganizationRequest) => createOrganization(token!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
}

export function useOrganizationProjects(organizationId: string) {
  const { token } = useAuth();
  return useQuery({
    queryKey: ["organization-projects", organizationId],
    queryFn: () => listOrganizationProjects(token!, organizationId),
    enabled: !!token && !!organizationId,
  });
}
