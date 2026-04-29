"use client";

import { useTranslations } from "next-intl";
import { SidebarLogo } from "@/components/atoms/sidebar/sidebar-logo";
import { SidebarNav } from "./sidebar-nav";
import { ProjectsSection } from "./projects-section";
import { OrganizationSection } from "./organization-section";
import { UserMenu } from "./user-menu";
import { useSidebarData } from "./use-sidebar-data";
import { FavoriteConversationsSection } from "./favorite-conversations-section";

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
        <FavoriteConversationsSection />
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
