"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  acceptUserOrganizationInvitation,
  listUserPendingOrganizationInvitations,
} from "@/lib/api/organizations";
import { useAuth } from "./use-auth";

export function useUserPendingOrganizationInvitations() {
  const { token } = useAuth();
  return useQuery({
    queryKey: ["user-pending-organization-invitations"],
    queryFn: () => listUserPendingOrganizationInvitations(token!),
    enabled: !!token,
  });
}

export function useAcceptUserOrganizationInvitation() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (invitationId: string) => acceptUserOrganizationInvitation(token!, invitationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-pending-organization-invitations"] });
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
}
