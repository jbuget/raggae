"use client";

import { useTranslations } from "next-intl";
import { SidebarLogo } from "./atoms/sidebar-logo";
import { SidebarNav } from "./organisms/sidebar-nav";
import { ProjectsSection } from "./organisms/projects-section";
import { OrganizationSection } from "./organisms/organization-section";
import { useSidebarData } from "./use-sidebar-data";

export function MobileSidebar() {
  const t = useTranslations("sidebar");
  const {
    personalProjects,
    isLoadingProjects,
    sortedOrganizations,
    organizationProjectsMap,
    editableOrganizationIds,
  } = useSidebarData();

  return (
    <div>
      <SidebarLogo />
      <nav className="space-y-1 p-4">
        <SidebarNav matchPrefix />
        <ProjectsSection
          variant="mobile"
          title={t("myProjects")}
          projects={personalProjects}
          isLoading={isLoadingProjects}
          canCreate
          createHref="/projects?create=1"
          createAriaLabel={t("createProject")}
        />
        {sortedOrganizations.map((org) => (
          <OrganizationSection
            key={org.id}
            variant="mobile"
            organization={org}
            projects={organizationProjectsMap.get(org.id) ?? []}
            canCreate={editableOrganizationIds.has(org.id)}
          />
        ))}
      </nav>
    </div>
  );
}
