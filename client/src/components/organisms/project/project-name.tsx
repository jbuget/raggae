"use client";

import { Skeleton } from "@/components/ui/skeleton";
import { useProject } from "@/lib/hooks/use-projects";

interface ProjectNameProps {
  projectId: string;
}

export function ProjectName({ projectId }: ProjectNameProps) {
  const { data: project, isLoading } = useProject(projectId);

  if (isLoading) return <Skeleton className="inline-block h-6 w-36" />;
  return <>{project?.name ?? ""}</>;
}
