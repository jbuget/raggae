import { useTranslations } from "next-intl";
import { ProjectsSection } from "./projects-section";
import type { OrganizationResponse, ProjectResponse } from "@/lib/types/api";

interface OrganizationSectionProps {
  variant: "desktop" | "mobile";
  organization: OrganizationResponse;
  projects: ProjectResponse[];
  canCreate: boolean;
}

export function OrganizationSection({
  variant,
  organization,
  projects,
  canCreate,
}: OrganizationSectionProps) {
  const t = useTranslations("sidebar");

  return (
    <ProjectsSection
      variant={variant}
      title={organization.name}
      projects={projects}
      canCreate={canCreate}
      createHref={`/projects?create=1&organizationId=${organization.id}`}
      createAriaLabel={t("createProjectIn", { orgName: organization.name })}
      canAccessSettings={canCreate}
    />
  );
}
