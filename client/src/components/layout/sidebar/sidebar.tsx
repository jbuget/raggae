"use client";

import { useTranslations } from "next-intl";
import { SidebarLogo } from "./atoms/sidebar-logo";
import { SidebarNav } from "./organisms/sidebar-nav";
import { ProjectsSection } from "./organisms/projects-section";
import { OrganizationSection } from "./organisms/organization-section";
import { UserMenu } from "./organisms/user-menu";
import { useSidebarData } from "./use-sidebar-data";

export function Sidebar() {
  const t = useTranslations("sidebar");
  const {
    personalProjects,
    isLoadingProjects,
    sortedOrganizations,
    organizationProjectsMap,
    editableOrganizationIds,
  } = useSidebarData();

  return (
    <aside className="hidden h-full w-64 border-r bg-white dark:bg-muted/30 md:flex md:flex-col">
      <SidebarLogo />
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        <SidebarNav showIcons />
        <ProjectsSection
          variant="desktop"
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
            variant="desktop"
            organization={org}
            projects={organizationProjectsMap.get(org.id) ?? []}
            canCreate={editableOrganizationIds.has(org.id)}
          />
        ))}
      </nav>
      <UserMenu />
    </aside>
  );
}
