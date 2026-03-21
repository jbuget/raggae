"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ProjectCard } from "./project-card";
import { ProjectWizard } from "./wizard/project-wizard";
import { useProjects } from "@/lib/hooks/use-projects";

export function ProjectList() {
  const t = useTranslations("projects");
  const router = useRouter();
  const searchParams = useSearchParams();
  const { data: projects, isLoading, error } = useProjects();
  const shouldOpenFromQuery = searchParams.get("create") === "1";
  const organizationIdFromQuery = searchParams.get("organizationId");
  const [wizardOpen, setWizardOpen] = useState(false);
  const effectiveWizardOpen = wizardOpen || shouldOpenFromQuery;

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-destructive">
        Failed to load projects
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("title")}</h1>
        <Button onClick={() => setWizardOpen(true)}>{t("new")}</Button>
      </div>

      <ProjectWizard
        open={effectiveWizardOpen}
        onOpenChange={(open) => {
          setWizardOpen(open);
          if (!open && shouldOpenFromQuery) {
            router.replace("/projects");
          }
        }}
        organizationId={organizationIdFromQuery}
      />

      {projects && projects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">{t("empty")}</p>
          <Button onClick={() => setWizardOpen(true)}>{t("list.createFirst")}</Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects?.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  );
}
