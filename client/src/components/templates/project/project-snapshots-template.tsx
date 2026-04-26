"use client";

import { useTranslations } from "next-intl";
import { PageTemplate } from "@/components/templates/page-template";
import { ProjectSnapshotsList } from "@/components/organisms/project/project-snapshots-list";

type ProjectSnapshotsTemplateProps = {
  projectId: string;
};

export function ProjectSnapshotsTemplate({ projectId }: ProjectSnapshotsTemplateProps) {
  const t = useTranslations("projects.snapshots");
  return (
    <PageTemplate title={t("title")} description={t("description")}>
      <ProjectSnapshotsList projectId={projectId} />
    </PageTemplate>
  );
}
