"use client";

import { useTranslations } from "next-intl";
import { useOrganization } from "@/lib/hooks/use-organization";
import { useProject } from "@/lib/hooks/use-projects";

interface ProjectOwnerNameProps {
  projectId: string;
}

export function ProjectOwnerName({ projectId }: ProjectOwnerNameProps) {
  const t = useTranslations("sidebar");
  const { data: project } = useProject(projectId);
  const { data: org } = useOrganization(project?.organization_id ?? "");

  if (!project) return null;
  if (project.organization_id && org) return <>{org.name}</>;
  return <>{t("myProjects")}</>;
}
