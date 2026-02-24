"use client";

import Link from "next/link";
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
  return (
    <Link href={`/projects/${project.id}/chat`} className="h-full">
      <Card className="h-full transition-colors hover:bg-muted/50">
        <CardHeader className="flex h-full flex-col">
          <CardTitle className="text-lg">{project.name}</CardTitle>
          <CardDescription className="line-clamp-3">
            {project.description || "No description"}
          </CardDescription>
          <p className="mt-auto pt-2 text-xs text-muted-foreground">
            Created {formatDate(project.created_at)}
          </p>
        </CardHeader>
      </Card>
    </Link>
  );
}
