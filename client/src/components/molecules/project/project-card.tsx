"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { MoreVertical, Settings } from "lucide-react";
import { useTranslations } from "next-intl";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import type { ProjectResponse } from "@/lib/types/api";
import { formatDate } from "@/lib/utils/format";

interface ProjectCardProps {
  project: ProjectResponse;
  showSettings?: boolean;
}

export function ProjectCard({ project, showSettings = true }: ProjectCardProps) {
  const t = useTranslations("projects");
  const tCommon = useTranslations("common");
  const router = useRouter();

  return (
    <div className="relative h-full">
      <Link href={`/projects/${project.id}/chat`} className="h-full">
        <Card className="h-full transition-colors hover:bg-muted/50">
          <CardHeader className="flex h-full flex-col pr-10">
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

      {showSettings && (
        <div className="absolute right-2 top-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
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
        </div>
      )}
    </div>
  );
}
