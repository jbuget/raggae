"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useProjects } from "@/lib/hooks/use-projects";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/projects", label: "Projects" },
];

export function MobileSidebar() {
  const pathname = usePathname();
  const { data: projects, isLoading } = useProjects();

  return (
    <div>
      <div className="flex h-14 items-center border-b px-6">
        <Link href="/projects" className="text-xl font-bold">
          Raggae
        </Link>
      </div>
      <nav className="space-y-1 p-4">
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
              <Link
                key={project.id}
                href={`/projects/${project.id}/chat`}
                className={cn(
                  "block truncate rounded-md px-3 py-2 text-sm transition-colors",
                  pathname.startsWith(`/projects/${project.id}`)
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
                title={project.name}
              >
                {project.name}
              </Link>
            ))}
        </div>
      </nav>
    </div>
  );
}
