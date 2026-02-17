"use client";

import Link from "next/link";
import { Github, MoreHorizontal } from "lucide-react";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useProjects } from "@/lib/hooks/use-projects";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/projects", label: "Projects", icon: "folder" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { data: projects, isLoading } = useProjects();
  const gitBranch = process.env.NEXT_PUBLIC_APP_GIT_BRANCH ?? "unknown";
  const gitCommit = process.env.NEXT_PUBLIC_APP_GIT_COMMIT ?? "unknown";
  const shortCommit = gitCommit === "unknown" ? gitCommit : gitCommit.slice(0, 7);

  return (
    <aside className="hidden h-full w-64 border-r bg-muted/30 md:flex md:flex-col">
      <div className="flex h-14 items-center border-b px-6">
        <Link href="/projects" className="text-xl font-bold">
          Raggae
        </Link>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-4">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              pathname.startsWith(item.href)
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            {item.label}
          </Link>
        ))}
        <div className="mt-4 border-t pt-3">
          <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            My Projects
          </p>
          {isLoading && (
            <p className="px-3 py-1 text-sm text-muted-foreground">Loading...</p>
          )}
          {!isLoading && projects?.length === 0 && (
            <p className="px-3 py-1 text-sm text-muted-foreground">No projects</p>
          )}
          {!isLoading &&
            projects?.map((project) => (
              <div
                key={project.id}
                className={cn(
                  "flex items-center gap-1 rounded-md px-1 py-1 text-sm transition-colors",
                  pathname.startsWith(`/projects/${project.id}`)
                    ? "bg-primary/10"
                    : "hover:bg-muted",
                )}
              >
                <Link
                  href={`/projects/${project.id}`}
                  className={cn(
                    "min-w-0 flex-1 truncate rounded-md px-2 py-1",
                    pathname.startsWith(`/projects/${project.id}`)
                      ? "text-primary"
                      : "text-muted-foreground hover:text-foreground",
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
                      className="h-7 w-7"
                      aria-label={`Project menu ${project.name}`}
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem asChild>
                      <Link href={`/projects/${project.id}/chat`}>Chat</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link href={`/projects/${project.id}/documents`}>Documents</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link href={`/projects/${project.id}/settings`}>Settings</Link>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ))}
        </div>
      </nav>
      <div className="border-t p-3">
        <a
          href="https://github.com/jbuget/raggae"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
        >
          <Github className="size-4" />
          <span>GitHub project</span>
        </a>
        <p className="mt-2 text-xs text-muted-foreground">
          {gitBranch}@{shortCommit}
        </p>
      </div>
    </aside>
  );
}
