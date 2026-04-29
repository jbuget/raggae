"use client";

import { useQueries } from "@tanstack/react-query";
import { listConversations } from "@/lib/api/chat";
import { useAuth } from "@/lib/hooks/use-auth";
import { useAccessibleProjects } from "@/lib/hooks/use-accessible-projects";

export function useSidebarData() {
  const { token } = useAuth();
  const {
    personalProjects,
    organizationSections,
    editableOrganizationIds,
    isLoading: isLoadingProjects,
  } = useAccessibleProjects();

  const sortedOrganizations = organizationSections.map((s) => s.organization);

  const organizationProjectsMap = new Map(
    organizationSections.map((s) => [s.organization.id, s.projects]),
  );

  const allOrgProjects = organizationSections.flatMap((s) => s.projects);
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
    allProjects,
    isLoadingProjects,
    sortedOrganizations,
    organizationProjectsMap,
    editableOrganizationIds,
  };
}
