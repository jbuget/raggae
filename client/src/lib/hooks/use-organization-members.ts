"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  inviteOrganizationMember,
  listOrganizationInvitations,
  listOrganizationMembers,
  removeOrganizationMember,
  resendOrganizationInvitation,
  revokeOrganizationInvitation,
  updateOrganizationMemberRole,
} from "@/lib/api/organizations";
import type {
  InviteOrganizationMemberRequest,
  OrganizationMemberRole,
} from "@/lib/types/api";
import { useAuth } from "./use-auth";

export function useOrganizationMembers(organizationId: string) {
  const { token } = useAuth();
  return useQuery({
    queryKey: ["organization-members", organizationId],
    queryFn: () => listOrganizationMembers(token!, organizationId),
    enabled: !!token && !!organizationId,
  });
}

export function useOrganizationInvitations(organizationId: string) {
  const { token } = useAuth();
  return useQuery({
    queryKey: ["organization-invitations", organizationId],
    queryFn: () => listOrganizationInvitations(token!, organizationId),
    enabled: !!token && !!organizationId,
  });
}

export function useInviteOrganizationMember(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: InviteOrganizationMemberRequest) =>
      inviteOrganizationMember(token!, organizationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization-invitations", organizationId] });
    },
  });
}

export function useUpdateOrganizationMemberRole(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ memberId, role }: { memberId: string; role: OrganizationMemberRole }) =>
      updateOrganizationMemberRole(token!, organizationId, memberId, { role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization-members", organizationId] });
    },
  });
}

export function useRemoveOrganizationMember(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (memberId: string) => removeOrganizationMember(token!, organizationId, memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization-members", organizationId] });
    },
  });
}

export function useResendOrganizationInvitation(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (invitationId: string) =>
      resendOrganizationInvitation(token!, organizationId, invitationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization-invitations", organizationId] });
    },
  });
}

export function useRevokeOrganizationInvitation(organizationId: string) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (invitationId: string) =>
      revokeOrganizationInvitation(token!, organizationId, invitationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization-invitations", organizationId] });
    },
  });
}
