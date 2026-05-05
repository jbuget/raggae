"use client";

import { ChevronRight } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useProject } from "@/lib/hooks/use-projects";
import { useOrganization } from "@/lib/hooks/use-organization";

interface ProjectNameProps {
  projectId: string;
  showOrg?: boolean;
}

export function ProjectName({ projectId, showOrg }: ProjectNameProps) {
  const { data: project, isLoading } = useProject(projectId);
  const { data: org } = useOrganization(project?.organization_id ?? "");

  if (isLoading) return <Skeleton className="inline-block h-6 w-36" />;

  const name = project?.name ?? "";
  if (showOrg && org) {
    return (
      <span className="inline-flex items-center gap-1.5">
        <span className="text-muted-foreground">{org.name}</span>
        <ChevronRight className="size-5 shrink-0 text-muted-foreground" />
        {name}
      </span>
    );
  }
  return <>{name}</>;
}
