"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useProject } from "@/lib/hooks/use-projects";

interface ProjectOverviewPanelProps {
  projectId: string;
}

export function ProjectOverviewPanel({ projectId }: ProjectOverviewPanelProps) {
  const t = useTranslations("projects");
  const { data: project, isLoading } = useProject(projectId);

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!project) {
    return <div className="text-center text-muted-foreground">{t("notFound")}</div>;
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <Link href={`/projects/${project.id}/chat`}>
        <Card className="transition-colors hover:bg-muted/50">
          <CardHeader>
            <CardTitle className="text-base">{t("page.chatTitle")}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{t("page.chatDescription")}</p>
          </CardContent>
        </Card>
      </Link>

      <Link href={`/projects/${project.id}/settings`}>
        <Card className="transition-colors hover:bg-muted/50">
          <CardHeader>
            <CardTitle className="text-base">{t("page.settingsTitle")}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{t("page.settingsDescription")}</p>
          </CardContent>
        </Card>
      </Link>
    </div>
  );
}
