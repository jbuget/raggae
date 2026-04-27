"use client";

import { useState } from "react";
import Link from "next/link";
import { ChevronRight, MessageSquare, MessageSquarePlus, MoreVertical, Settings } from "lucide-react";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { Collapsible } from "radix-ui";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import type { ProjectResponse } from "@/lib/types/api";
import { ProjectConversationList } from "./project-conversation-list";

interface DesktopProjectItemProps {
  project: ProjectResponse;
  canAccessSettings?: boolean;
}

export function DesktopProjectItem({ project, canAccessSettings = true }: DesktopProjectItemProps) {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const t = useTranslations("sidebar");
  const isActive = pathname.startsWith(`/projects/${project.id}`);

  return (
    <Collapsible.Root open={isOpen} onOpenChange={setIsOpen}>
      <div
        className={cn(
          "group flex items-center gap-1 rounded-md px-1 py-1 text-sm transition-colors",
          isActive ? "" : "hover:bg-muted",
        )}
      >
        <Collapsible.Trigger asChild>
          <button
            type="button"
            className={cn(
              "flex min-w-0 flex-1 cursor-pointer items-center gap-1 truncate rounded-md px-2 text-left",
              isActive ? "font-semibold text-foreground" : "text-muted-foreground hover:text-foreground",
            )}
            title={project.name}
          >
            <ChevronRight
              className={cn(
                "h-3 w-3 shrink-0 transition-transform duration-200",
                isOpen && "rotate-90",
              )}
            />
            <span className="truncate">{project.name}</span>
          </button>
        </Collapsible.Trigger>
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
              <Link href={`/projects/${project.id}/chat`}>
                <MessageSquarePlus className="h-4 w-4" />
                {t("newConversation")}
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild className="cursor-pointer">
              <Link href={`/projects/${project.id}/conversations`}>
                <MessageSquare className="h-4 w-4" />
                {t("conversations")}
              </Link>
            </DropdownMenuItem>
            {canAccessSettings && (
              <DropdownMenuItem asChild className="cursor-pointer">
                <Link href={`/projects/${project.id}/settings`}>
                  <Settings className="h-4 w-4" />
                  {t("settings")}
                </Link>
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <Collapsible.Content className="overflow-hidden data-[state=open]:animate-collapsible-down data-[state=closed]:animate-collapsible-up">
        <div className="ml-2 mt-0.5">
          <ProjectConversationList projectId={project.id} />
        </div>
      </Collapsible.Content>
    </Collapsible.Root>
  );
}
