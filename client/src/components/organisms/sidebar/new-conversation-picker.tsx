"use client";

import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Check, MessageSquarePlus, Search } from "lucide-react";
import { useTranslations } from "next-intl";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useSidebarData } from "./use-sidebar-data";

interface NewConversationPickerProps {
  showIcon?: boolean;
}

export function NewConversationPicker({ showIcon = false }: NewConversationPickerProps) {
  const t = useTranslations("sidebar");
  const router = useRouter();
  const pathname = usePathname();
  const { allProjects } = useSidebarData();

  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");

  const currentProjectId = pathname.match(/^\/projects\/([^/]+)/)?.[1] ?? null;

  const filteredProjects = allProjects.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()),
  );

  function handleSelect(projectId: string) {
    router.push(`/projects/${projectId}/chat`);
    setOpen(false);
    setSearch("");
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          type="button"
          className={cn(
            "flex w-full cursor-pointer items-center gap-3 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
            "text-muted-foreground hover:bg-muted hover:text-foreground",
          )}
          aria-label={t("newConversation")}
        >
          {showIcon && <MessageSquarePlus size={16} />}
          {t("newConversation")}
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-2" align="start">
        <div className="mb-1 flex items-center gap-2 rounded-md border px-2 py-1">
          <Search className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("searchProjects")}
            className="h-6 border-0 bg-transparent p-0 text-sm shadow-none focus-visible:ring-0"
          />
        </div>
        <ScrollArea className="max-h-60" onWheel={(e) => e.stopPropagation()}>
          {filteredProjects.length === 0 && (
            <p className="px-2 py-1.5 text-xs text-muted-foreground">{t("noProjectsFound")}</p>
          )}
          {filteredProjects.map((project) => {
            const isCurrent = project.id === currentProjectId;
            return (
              <button
                key={project.id}
                type="button"
                onClick={() => handleSelect(project.id)}
                className={cn(
                  "flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm",
                  isCurrent
                    ? "bg-accent text-accent-foreground font-medium cursor-pointer"
                    : "hover:bg-accent hover:text-accent-foreground cursor-pointer",
                )}
                aria-label={project.name}
              >
                {isCurrent ? (
                  <Check className="h-3 w-3 shrink-0" />
                ) : (
                  <span className="h-3 w-3 shrink-0" />
                )}
                <span className="truncate">{project.name}</span>
              </button>
            );
          })}
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
