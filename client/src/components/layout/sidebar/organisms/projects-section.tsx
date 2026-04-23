"use client";

import { useTranslations } from "next-intl";
import { SidebarSectionHeader } from "../atoms/sidebar-section-header";
import { DesktopProjectItem } from "../molecules/desktop-project-item";
import { MobileProjectItem } from "../molecules/mobile-project-item";
import type { ProjectResponse } from "@/lib/types/api";

interface ProjectsSectionProps {
  variant: "desktop" | "mobile";
  title: string;
  projects: ProjectResponse[];
  isLoading?: boolean;
  canCreate: boolean;
  createHref: string;
  createAriaLabel: string;
  canAccessSettings?: boolean;
}

export function ProjectsSection({
  variant,
  title,
  projects,
  isLoading = false,
  canCreate,
  createHref,
  createAriaLabel,
  canAccessSettings = true,
}: ProjectsSectionProps) {
  const t = useTranslations("sidebar");
  const tCommon = useTranslations("common");

  return (
    <div className="mt-2 border-t pt-2">
      <SidebarSectionHeader
        title={title}
        canCreate={canCreate}
        createHref={createHref}
        createAriaLabel={createAriaLabel}
      />
      {isLoading && (
        <p className="px-3 py-1 text-sm text-muted-foreground">{tCommon("loading")}</p>
      )}
      {!isLoading && projects.length === 0 && (
        <p className="px-3 py-1 text-sm text-muted-foreground">{t("noProjects")}</p>
      )}
      {!isLoading &&
        projects.map((project) =>
          variant === "desktop" ? (
            <DesktopProjectItem
              key={project.id}
              project={project}
              canAccessSettings={canAccessSettings}
            />
          ) : (
            <MobileProjectItem key={project.id} project={project} />
          ),
        )}
    </div>
  );
}
