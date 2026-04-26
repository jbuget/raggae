"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { ProjectResponse } from "@/lib/types/api";
import { formatDate } from "@/lib/utils/format";

interface ProjectCardProps {
  project: ProjectResponse;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const t = useTranslations("projects");
  const tCommon = useTranslations("common");

  return (
    <Link href={`/projects/${project.id}/chat`} className="h-full">
      <Card className="h-full transition-colors hover:bg-muted/50">
        <CardHeader className="flex h-full flex-col">
          <CardTitle className="text-lg">{project.name}</CardTitle>
          <CardDescription className="line-clamp-3">
            {project.description || tCommon("noDescription")}
          </CardDescription>
          <p className="mt-auto pt-2 text-xs text-muted-foreground">
            {t("card.created")} {formatDate(project.created_at)}
          </p>
        </CardHeader>
      </Card>
    </Link>
  );
}
