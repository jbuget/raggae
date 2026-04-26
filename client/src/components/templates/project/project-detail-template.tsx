"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { PageTemplate } from "@/components/templates/page-template";
import { useProject } from "@/lib/hooks/use-projects";

type ProjectDetailTemplateProps = {
  projectId: string;
};

export function ProjectDetailTemplate({ projectId }: ProjectDetailTemplateProps) {
  const t = useTranslations("projects");
  const { data: project, isLoading } = useProject(projectId);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!project) {
    return <div className="text-center text-muted-foreground">{t("notFound")}</div>;
  }

  return (
    <PageTemplate
      title={project.name}
      description={project.description ?? undefined}
      actions={
        <Button asChild variant="outline" size="sm">
          <Link href={`/projects/${project.id}/settings`}>{t("page.settings")}</Link>
        </Button>
      }
    >
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
    </PageTemplate>
  );
}
