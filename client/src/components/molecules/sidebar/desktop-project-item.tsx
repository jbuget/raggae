"use client";

import Link from "next/link";
import { MoreVertical } from "lucide-react";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import type { ProjectResponse } from "@/lib/types/api";

interface DesktopProjectItemProps {
  project: ProjectResponse;
  canAccessSettings?: boolean;
}

export function DesktopProjectItem({ project, canAccessSettings = true }: DesktopProjectItemProps) {
  const pathname = usePathname();
  const t = useTranslations("sidebar");
  const isActive = pathname.startsWith(`/projects/${project.id}`);

  return (
    <div
      className="group flex items-center gap-1 rounded-md px-1 py-1 text-sm transition-colors hover:bg-muted"
    >
      <Link
        href={`/projects/${project.id}/chat`}
        className={cn(
          "min-w-0 flex-1 truncate rounded-md px-2",
          isActive ? "font-semibold text-foreground" : "text-muted-foreground hover:text-foreground",
        )}
        title={project.name}
      >
        {project.name}
      </Link>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "h-5 w-5 cursor-pointer opacity-0 transition-opacity group-hover:opacity-100 data-[state=open]:opacity-100",
              !isActive && "hover:bg-primary/10",
            )}
            aria-label={t("projectMenu", { projectName: project.name })}
          >
            <MoreVertical className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem asChild className="cursor-pointer">
            <Link href={`/projects/${project.id}/chat`}>{t("chat")}</Link>
          </DropdownMenuItem>
          {canAccessSettings && (
            <DropdownMenuItem asChild className="cursor-pointer">
              <Link href={`/projects/${project.id}/settings`}>{t("settings")}</Link>
            </DropdownMenuItem>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
