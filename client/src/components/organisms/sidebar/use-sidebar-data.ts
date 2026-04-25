"use client";

import { useQueries } from "@tanstack/react-query";
import { listConversations } from "@/lib/api/chat";
import { listOrganizationMembers, listOrganizationProjects } from "@/lib/api/organizations";
import { useAuth } from "@/lib/hooks/use-auth";
import { useOrganizations } from "@/lib/hooks/use-organizations";
import { useProjects } from "@/lib/hooks/use-projects";

export function useSidebarData() {
  const { token, user } = useAuth();
  const { data: projects, isLoading: isLoadingProjects } = useProjects();
  const { data: organizations } = useOrganizations();

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

  const organizationProjectsMap = new Map(
    sortedOrganizations.map((organization, index) => [
      organization.id,
      organizationProjectsQueries[index]?.data ?? [],
    ]),
  );

  const organizationMembersQueries = useQueries({
    queries: sortedOrganizations.map((organization) => ({
      queryKey: ["organization-members", organization.id],
      queryFn: () => listOrganizationMembers(token!, organization.id),
      enabled: !!token && !!user?.id,
    })),
  });

  const editableOrganizationIds = new Set(
    sortedOrganizations
      .filter((_, index) => {
        const members = organizationMembersQueries[index]?.data ?? [];
        const currentUserMember = members.find((member) => member.user_id === user?.id);
        return currentUserMember?.role === "owner" || currentUserMember?.role === "maker";
      })
      .map((organization) => organization.id),
  );

  const personalProjects = (projects ?? []).filter((p) => !p.organization_id);

  const allOrgProjects = Array.from(organizationProjectsMap.values()).flat();
  const allProjects = [...personalProjects, ...allOrgProjects];

  useQueries({
    queries: allProjects.map((project) => ({
      queryKey: ["conversations", project.id, 10],
      queryFn: () => listConversations(token!, project.id, 10),
      enabled: !!token,
    })),
  });

  return {
    personalProjects,
    isLoadingProjects,
    sortedOrganizations,
    organizationProjectsMap,
    editableOrganizationIds,
  };
}
