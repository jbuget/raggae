"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { MoreVertical, Settings } from "lucide-react";
import { useTranslations } from "next-intl";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import type { ProjectResponse } from "@/lib/types/api";
import { formatDate } from "@/lib/utils/format";

interface ProjectListItemProps {
  project: ProjectResponse;
  showSettings?: boolean;
}

export function ProjectListItem({ project, showSettings = true }: ProjectListItemProps) {
  const t = useTranslations("projects");
  const tCommon = useTranslations("common");
  const router = useRouter();

  return (
    <div className="relative flex items-center gap-4 rounded-lg border px-4 py-3 transition-colors hover:bg-muted/50">
      <Link
        href={`/projects/${project.id}/chat`}
        className="flex flex-1 items-center gap-4 min-w-0"
      >
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{project.name}</p>
          <p className="text-sm text-muted-foreground truncate">
            {project.description || tCommon("noDescription")}
          </p>
        </div>
        <p className="shrink-0 text-xs text-muted-foreground">
          {t("card.created")} {formatDate(project.created_at)}
        </p>
      </Link>

      {showSettings && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 shrink-0"
              onClick={(e) => e.preventDefault()}
            >
              <MoreVertical className="size-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => router.push(`/projects/${project.id}/settings`)}>
              <Settings className="mr-2 size-4" />
              {t("card.settings")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </div>
  );
}
