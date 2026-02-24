"use client";

import Link from "next/link";
import { Plus } from "lucide-react";
import { usePathname } from "next/navigation";
import { useQueries } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { useProjects } from "@/lib/hooks/use-projects";
import { useAuth } from "@/lib/hooks/use-auth";
import { listOrganizationProjects } from "@/lib/api/organizations";
import { useOrganizations } from "@/lib/hooks/use-organizations";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/projects", label: "Projects" },
  { href: "/organizations", label: "Organizations" },
];

export function MobileSidebar() {
  const pathname = usePathname();
  const { token } = useAuth();
  const { data: projects, isLoading } = useProjects();
  const { data: organizations } = useOrganizations();
  const organizationProjectsQueries = useQueries({
    queries: (organizations ?? []).map((organization) => ({
      queryKey: ["organization-projects", organization.id],
      queryFn: () => listOrganizationProjects(token!, organization.id),
      enabled: !!token,
    })),
  });
  const organizationProjectsMap = new Map(
    (organizations ?? []).map((organization, index) => [
      organization.id,
      organizationProjectsQueries[index]?.data ?? [],
    ]),
  );

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
          <div className="flex h-7 items-center justify-between px-1 pb-2">
            <p className="px-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              My Projects
            </p>
            <Button asChild variant="ghost" size="icon" className="h-7 w-7">
              <Link href="/projects?create=1" aria-label="Create project">
                <Plus className="h-4 w-4" />
              </Link>
            </Button>
          </div>
          {isLoading && (
            <p className="px-3 py-1 text-sm text-muted-foreground">Loading...</p>
          )}
          {!isLoading && projects?.length === 0 && (
            <p className="px-3 py-1 text-sm text-muted-foreground">No projects</p>
          )}
          {!isLoading &&
            projects
              ?.filter((project) => !project.organization_id)
              .map((project) => (
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
        {(organizations ?? []).map((organization) => (
          <div key={organization.id} className="mt-4 border-t pt-3">
            <div className="flex h-7 items-center justify-between px-1 pb-2">
              <p
                className="truncate px-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground"
                title={organization.name}
              >
                {organization.name}
              </p>
              <Button asChild variant="ghost" size="icon" className="h-7 w-7">
                <Link
                  href={`/projects?create=1&organizationId=${organization.id}`}
                  aria-label={`Create project in ${organization.name}`}
                >
                  <Plus className="h-4 w-4" />
                </Link>
              </Button>
            </div>
            {(organizationProjectsMap.get(organization.id) ?? []).length === 0 ? (
              <p className="px-3 py-1 text-sm text-muted-foreground">No projects</p>
            ) : (
              (organizationProjectsMap.get(organization.id) ?? []).map((project) => (
                <Link
                  key={project.id}
                  href={`/projects/${project.id}/chat`}
                  className={cn(
                    "mx-1 block truncate rounded-md px-3 py-2 text-sm transition-colors",
                    pathname.startsWith(`/projects/${project.id}`)
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )}
                  title={project.name}
                >
                  {project.name}
                </Link>
              ))
            )}
          </div>
        ))}
      </nav>
    </div>
  );
}
