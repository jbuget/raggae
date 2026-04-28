"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { PageTemplate } from "@/components/templates/page-template";
import { ProjectOverviewPanel } from "@/components/organisms/project/project-overview-panel";
import { ProjectName } from "@/components/organisms/project/project-name";

type ProjectDetailTemplateProps = {
  projectId: string;
};

export function ProjectDetailTemplate({ projectId }: ProjectDetailTemplateProps) {
  const t = useTranslations("projects");

  return (
    <PageTemplate
      title={<ProjectName projectId={projectId} />}
      actions={
        <Button asChild variant="outline" size="sm">
          <Link href={`/projects/${projectId}/settings`}>{t("page.settings")}</Link>
        </Button>
      }
    >
      <ProjectOverviewPanel projectId={projectId} />
    </PageTemplate>
  );
}
