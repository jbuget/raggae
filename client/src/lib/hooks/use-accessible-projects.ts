"use client";

import { useQuery } from "@tanstack/react-query";
import { listAccessibleProjects } from "@/lib/api/projects";
import { useAuth } from "@/lib/hooks/use-auth";
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
  error: Error | null;
}

export function useAccessibleProjects(): AccessibleProjects {
  const { token } = useAuth();

  const { data, isLoading, error } = useQuery({
    queryKey: ["accessible-projects"],
    queryFn: () => listAccessibleProjects(token!),
    enabled: !!token,
  });

  const personalProjects = data?.personal_projects ?? [];

  const organizationSections: OrganizationSection[] = (
    data?.organization_sections ?? []
  ).map((section) => ({
    organization: {
      id: section.organization_id,
      name: section.organization_name,
      slug: null,
      description: null,
      logo_url: null,
      created_by_user_id: "",
      created_at: "",
      updated_at: "",
    },
    projects: section.projects,
    canEdit: section.can_edit,
  }));

  const editableOrganizationIds = new Set(
    organizationSections.filter((s) => s.canEdit).map((s) => s.organization.id),
  );

  return {
    personalProjects,
    organizationSections,
    editableOrganizationIds,
    isLoading,
    error: error as Error | null,
  };
}
