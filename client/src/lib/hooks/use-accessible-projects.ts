"use client";

import { useQueries } from "@tanstack/react-query";
import { listOrganizationMembers, listOrganizationProjects } from "@/lib/api/organizations";
import { useAuth } from "@/lib/hooks/use-auth";
import { useOrganizations } from "@/lib/hooks/use-organizations";
import { useProjects } from "@/lib/hooks/use-projects";
import type { OrganizationResponse, ProjectResponse } from "@/lib/types/api";

export interface OrganizationSection {
  organization: OrganizationResponse;
  projects: ProjectResponse[];
  canEdit: boolean;
}

export interface AccessibleProjects {
  personalProjects: ProjectResponse[];
  /** All org sections (including empty ones) — filter client-side when needed */
  organizationSections: OrganizationSection[];
  editableOrganizationIds: Set<string>;
  isLoading: boolean;
}

export function useAccessibleProjects(): AccessibleProjects {
  const { token, user } = useAuth();
  const { data: projects, isLoading: isLoadingProjects } = useProjects();
  const { data: organizations, isLoading: isLoadingOrgs } = useOrganizations();

  const sortedOrganizations = [...(organizations ?? [])].sort((a, b) =>
    a.name.localeCompare(b.name, undefined, { sensitivity: "base" }),
  );

  const organizationProjectsQueries = useQueries({
    queries: sortedOrganizations.map((organization) => ({
      queryKey: ["organization-projects", organization.id],
      queryFn: () => listOrganizationProjects(token!, organization.id),
      enabled: !!token,
    })),
  });

  const organizationMembersQueries = useQueries({
    queries: sortedOrganizations.map((organization) => ({
      queryKey: ["organization-members", organization.id],
      queryFn: () => listOrganizationMembers(token!, organization.id),
      enabled: !!token && !!user?.id,
    })),
  });

  const personalProjects = (projects ?? []).filter((p) => !p.organization_id);

  const organizationSections: OrganizationSection[] = sortedOrganizations.map(
    (organization, index) => {
      const orgProjects = organizationProjectsQueries[index]?.data ?? [];
      const members = organizationMembersQueries[index]?.data ?? [];
      const currentUserMember = members.find((m) => m.user_id === user?.id);
      const canEdit =
        currentUserMember?.role === "owner" || currentUserMember?.role === "maker";
      return { organization, projects: orgProjects, canEdit };
    },
  );

  const editableOrganizationIds = new Set(
    organizationSections.filter((s) => s.canEdit).map((s) => s.organization.id),
  );

  const isLoading =
    isLoadingProjects ||
    isLoadingOrgs ||
    organizationProjectsQueries.some((q) => q.isLoading) ||
    organizationMembersQueries.some((q) => q.isLoading);

  return { personalProjects, organizationSections, editableOrganizationIds, isLoading };
}
