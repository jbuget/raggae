import type {
  AcceptOrganizationInvitationRequest,
  CreateOrganizationRequest,
  InviteOrganizationMemberRequest,
  OrganizationInvitationResponse,
  OrganizationMemberResponse,
  ProjectResponse,
  OrganizationResponse,
  UpdateOrganizationMemberRoleRequest,
  UpdateOrganizationRequest,
} from "@/lib/types/api";
import { apiFetch } from "./client";

export function listOrganizations(token: string): Promise<OrganizationResponse[]> {
  return apiFetch<OrganizationResponse[]>("/organizations", { token });
}

export function createOrganization(
  token: string,
  data: CreateOrganizationRequest,
): Promise<OrganizationResponse> {
  return apiFetch<OrganizationResponse>("/organizations", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function getOrganization(
  token: string,
  organizationId: string,
): Promise<OrganizationResponse> {
  return apiFetch<OrganizationResponse>(`/organizations/${organizationId}`, { token });
}

export function updateOrganization(
  token: string,
  organizationId: string,
  data: UpdateOrganizationRequest,
): Promise<OrganizationResponse> {
  return apiFetch<OrganizationResponse>(`/organizations/${organizationId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
    token,
  });
}

export function deleteOrganization(token: string, organizationId: string): Promise<void> {
  return apiFetch<void>(`/organizations/${organizationId}`, {
    method: "DELETE",
    token,
  });
}

export function listOrganizationMembers(
  token: string,
  organizationId: string,
): Promise<OrganizationMemberResponse[]> {
  return apiFetch<OrganizationMemberResponse[]>(
    `/organizations/${organizationId}/members`,
    { token },
  );
}

export function listOrganizationProjects(
  token: string,
  organizationId: string,
): Promise<ProjectResponse[]> {
  return apiFetch<ProjectResponse[]>(
    `/organizations/${organizationId}/projects`,
    { token },
  );
}

export function updateOrganizationMemberRole(
  token: string,
  organizationId: string,
  memberId: string,
  data: UpdateOrganizationMemberRoleRequest,
): Promise<OrganizationMemberResponse> {
  return apiFetch<OrganizationMemberResponse>(
    `/organizations/${organizationId}/members/${memberId}`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
      token,
    },
  );
}

export function removeOrganizationMember(
  token: string,
  organizationId: string,
  memberId: string,
): Promise<void> {
  return apiFetch<void>(`/organizations/${organizationId}/members/${memberId}`, {
    method: "DELETE",
    token,
  });
}

export function leaveOrganization(token: string, organizationId: string): Promise<void> {
  return apiFetch<void>(`/organizations/${organizationId}/leave`, {
    method: "POST",
    token,
  });
}

export function inviteOrganizationMember(
  token: string,
  organizationId: string,
  data: InviteOrganizationMemberRequest,
): Promise<OrganizationInvitationResponse> {
  return apiFetch<OrganizationInvitationResponse>(
    `/organizations/${organizationId}/invitations`,
    {
      method: "POST",
      body: JSON.stringify(data),
      token,
    },
  );
}

export function listOrganizationInvitations(
  token: string,
  organizationId: string,
): Promise<OrganizationInvitationResponse[]> {
  return apiFetch<OrganizationInvitationResponse[]>(
    `/organizations/${organizationId}/invitations`,
    { token },
  );
}

export function resendOrganizationInvitation(
  token: string,
  organizationId: string,
  invitationId: string,
): Promise<OrganizationInvitationResponse> {
  return apiFetch<OrganizationInvitationResponse>(
    `/organizations/${organizationId}/invitations/${invitationId}/resend`,
    {
      method: "POST",
      token,
    },
  );
}

export function revokeOrganizationInvitation(
  token: string,
  organizationId: string,
  invitationId: string,
): Promise<OrganizationInvitationResponse> {
  return apiFetch<OrganizationInvitationResponse>(
    `/organizations/${organizationId}/invitations/${invitationId}`,
    {
      method: "DELETE",
      token,
    },
  );
}

export function acceptOrganizationInvitation(
  token: string,
  data: AcceptOrganizationInvitationRequest,
): Promise<OrganizationMemberResponse> {
  return apiFetch<OrganizationMemberResponse>("/organizations/invitations/accept", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}
