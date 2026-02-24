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
    <Link href={`/projects/${project.id}/chat`}>
      <Card className="transition-colors hover:bg-muted/50">
        <CardHeader>
          <CardTitle className="text-lg">{project.name}</CardTitle>
          <CardDescription>
            {project.description || "No description"}
          </CardDescription>
          <p className="text-xs text-muted-foreground">
            Created {formatDate(project.created_at)}
          </p>
        </CardHeader>
      </Card>
    </Link>
  );
}
