"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import type { ProjectResponse } from "@/lib/types/api";
import { ProjectConversationList } from "./project-conversation-list";

interface MobileProjectItemProps {
  project: ProjectResponse;
}

export function MobileProjectItem({ project }: MobileProjectItemProps) {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const isActive = pathname.startsWith(`/projects/${project.id}`);

  return (
    <div>
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className={cn(
          "flex w-full cursor-pointer items-center gap-1 truncate rounded-md px-3 py-2 text-sm transition-colors",
          isActive
            ? "bg-primary/10 text-primary"
            : "text-muted-foreground hover:bg-muted hover:text-foreground",
        )}
        title={project.name}
      >
        {isOpen ? (
          <ChevronDown className="h-3 w-3 shrink-0" />
        ) : (
          <ChevronRight className="h-3 w-3 shrink-0" />
        )}
        <span className="truncate">{project.name}</span>
      </button>
      {isOpen && (
        <div className="ml-2 mt-0.5">
          <ProjectConversationList projectId={project.id} />
        </div>
      )}
    </div>
  );
}
