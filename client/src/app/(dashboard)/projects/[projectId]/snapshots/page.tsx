"use client";

import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { ProjectSnapshotsList } from "@/components/projects/project-snapshots-list";

export default function ProjectSnapshotsPage() {
  const t = useTranslations("projects.snapshots");
  const params = useParams<{ projectId: string }>();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t("title")}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{t("description")}</p>
      </div>

      <ProjectSnapshotsList projectId={params.projectId} />
    </div>
  );
}
