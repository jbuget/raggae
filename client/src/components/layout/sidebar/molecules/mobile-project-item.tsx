"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import type { ProjectResponse } from "@/lib/types/api";

interface MobileProjectItemProps {
  project: ProjectResponse;
}

export function MobileProjectItem({ project }: MobileProjectItemProps) {
  const pathname = usePathname();
  const isActive = pathname.startsWith(`/projects/${project.id}`);

  return (
    <Link
      href={`/projects/${project.id}/chat`}
      className={cn(
        "block truncate rounded-md px-3 py-2 text-sm transition-colors",
        isActive
          ? "bg-primary/10 text-primary"
          : "text-muted-foreground hover:bg-muted hover:text-foreground",
      )}
      title={project.name}
    >
      {project.name}
    </Link>
  );
}
