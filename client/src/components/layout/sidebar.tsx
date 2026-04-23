"use client";

import Link from "next/link";
import { signOut } from "next-auth/react";
import { Building2, Check, FolderOpen, Github, Languages, LogOut, Mail, Monitor, Moon, MoreVertical, Plus, Settings, Sun } from "lucide-react";
import { usePathname } from "next/navigation";
import { useQueries } from "@tanstack/react-query";
import { useLocale, useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useProjects } from "@/lib/hooks/use-projects";
import { useAuth } from "@/lib/hooks/use-auth";
import { listOrganizationMembers, listOrganizationProjects } from "@/lib/api/organizations";
import { useOrganizations } from "@/lib/hooks/use-organizations";
import type { Theme } from "@/lib/providers/theme-provider";
import { useTheme } from "@/lib/providers/theme-provider";
import { useUpdateUserLocale } from "@/lib/hooks/use-user-profile";
import type { UpdateUserLocaleRequest } from "@/lib/types/api";
import { cn } from "@/lib/utils";

const LOCALES: Array<{ value: UpdateUserLocaleRequest["locale"]; label: string }> = [
  { value: "en", label: "English" },
  { value: "fr", label: "Français" },
];

function setLocaleCookie(locale: string) {
  const maxAge = 60 * 60 * 24 * 365;
  document.cookie = `raggae_locale=${locale};path=/;max-age=${maxAge};SameSite=Lax`;
}

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations("sidebar");
  const tHeader = useTranslations("header");
  const tNav = useTranslations("nav");
  const tCommon = useTranslations("common");
  const tTheme = useTranslations("layout.themeToggle");
  const { theme, setTheme } = useTheme();
  const currentLocale = useLocale();
  const updateLocale = useUpdateUserLocale();

  const THEMES: Array<{ value: Theme; label: string; icon: React.ReactNode }> = [
    { value: "light", label: tTheme("light"), icon: <Sun size={14} /> },
    { value: "dark", label: tTheme("dark"), icon: <Moon size={14} /> },
    { value: "system", label: tTheme("system"), icon: <Monitor size={14} /> },
  ];

  function handleThemeSelect(next: Theme) {
    if (next !== theme) setTheme(next);
  }

  function handleLocaleSelect(locale: UpdateUserLocaleRequest["locale"]) {
    if (locale === currentLocale) return;
    setLocaleCookie(locale);
    updateLocale.mutate({ locale }, { onSettled: () => window.location.reload() });
  }

  const navItems = [
    { href: "/projects", label: tNav("projects"), icon: <FolderOpen size={16} /> },
    { href: "/organizations", label: tNav("organizations"), icon: <Building2 size={16} /> },
    { href: "/invitations", label: tNav("invitations"), icon: <Mail size={16} /> },
  ];
  const { token, user } = useAuth();
  const { data: projects, isLoading } = useProjects();
  const { data: organizations } = useOrganizations();
  const sortedOrganizations = [...(organizations ?? [])].sort((a, b) =>
    a.name.localeCompare(b.name, undefined, { sensitivity: "base" }),
  );
  const organizationProjectsQueries = useQueries({
    queries: sortedOrganizations.map((organization) => ({
      queryKey: ["organization-projects", organization.id],
      queryFn: () => listOrganizationProjects(token!, organization.id),
      enabled: !!token,
    })),
  });
  const organizationProjectsMap = new Map(
    sortedOrganizations.map((organization, index) => [
      organization.id,
      organizationProjectsQueries[index]?.data ?? [],
    ]),
  );
  const organizationMembersQueries = useQueries({
    queries: sortedOrganizations.map((organization) => ({
      queryKey: ["organization-members", organization.id],
      queryFn: () => listOrganizationMembers(token!, organization.id),
      enabled: !!token && !!user?.id,
    })),
  });
  const editableOrganizationIds = new Set(
    sortedOrganizations
      .filter((_, index) => {
        const members = organizationMembersQueries[index]?.data ?? [];
        const currentUserMember = members.find((member) => member.user_id === user?.id);
        return (
          currentUserMember?.role === "owner" || currentUserMember?.role === "maker"
        );
      })
      .map((organization) => organization.id),
  );
  const gitBranch = process.env.NEXT_PUBLIC_APP_GIT_BRANCH ?? "unknown";
  const gitCommit = process.env.NEXT_PUBLIC_APP_GIT_COMMIT ?? "unknown";
  const shortCommit = gitCommit === "unknown" ? gitCommit : gitCommit.slice(0, 7);

  return (
    <aside className="hidden h-full w-64 border-r bg-white dark:bg-muted/30 md:flex md:flex-col">
      <div className="flex h-14 items-center border-b px-6">
        <Link href="/projects" className="text-xl font-bold">
          Raggae
        </Link>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "mb-0 flex items-center gap-3 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              pathname === item.href
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            {item.icon}
            {item.label}
          </Link>
        ))}
        <div className="mt-2 border-t pt-2">
          <div className="flex h-6 items-center justify-between px-1 pb-1">
            <p className="px-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {t("myProjects")}
            </p>
            <Button asChild variant="ghost" size="icon" className="h-7 w-7">
              <Link href="/projects?create=1" aria-label={t("createProject")}>
                <Plus className="h-4 w-4" />
              </Link>
            </Button>
          </div>
          {isLoading && (
            <p className="px-3 py-1 text-sm text-muted-foreground">{tCommon("loading")}</p>
          )}
          {!isLoading && projects?.length === 0 && (
            <p className="px-3 py-1 text-sm text-muted-foreground">{t("noProjects")}</p>
          )}
          {!isLoading &&
            projects
              ?.filter((project) => !project.organization_id)
              .map((project) => (
              <div
                key={project.id}
                className={cn(
                  "group flex items-center gap-1 rounded-md px-1 py-1 text-sm transition-colors",
                  pathname.startsWith(`/projects/${project.id}`)
                    ? "bg-primary/10"
                    : "hover:bg-muted",
                )}
              >
                <Link
                  href={`/projects/${project.id}/chat`}
                  className={cn(
                    "min-w-0 flex-1 truncate rounded-md px-2",
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
                      className={cn(
                        "h-5 w-5 cursor-pointer opacity-0 transition-opacity group-hover:opacity-100 data-[state=open]:opacity-100",
                        !pathname.startsWith(`/projects/${project.id}`) && "hover:bg-primary/10",
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
                    <DropdownMenuItem asChild className="cursor-pointer">
                      <Link href={`/projects/${project.id}/settings`}>{t("settings")}</Link>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
              ))}
        </div>
        {sortedOrganizations.map((organization) => (
          <div key={organization.id} className="mt-2 border-t pt-2">
            <div className="flex h-6 items-center justify-between px-1 pb-1">
              <p
                className="truncate px-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground"
                title={organization.name}
              >
                {organization.name}
              </p>
              {editableOrganizationIds.has(organization.id) && (
                <Button asChild variant="ghost" size="icon" className="h-7 w-7">
                  <Link
                    href={`/projects?create=1&organizationId=${organization.id}`}
                    aria-label={t("createProjectIn", { orgName: organization.name })}
                  >
                    <Plus className="h-4 w-4" />
                  </Link>
                </Button>
              )}
            </div>
            {(organizationProjectsMap.get(organization.id) ?? []).length === 0 ? (
              <p className="px-3 py-1 text-sm text-muted-foreground">{t("noProjects")}</p>
            ) : (
              (organizationProjectsMap.get(organization.id) ?? []).map((project) => (
                <div
                  key={project.id}
                  className={cn(
                    "group flex items-center gap-1 rounded-md px-1 py-1 text-sm transition-colors",
                    pathname.startsWith(`/projects/${project.id}`)
                      ? "bg-primary/10"
                      : "hover:bg-muted",
                  )}
                >
                  <Link
                    href={`/projects/${project.id}/chat`}
                    className={cn(
                      "min-w-0 flex-1 truncate rounded-md px-2",
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
                        className={cn(
                          "h-5 w-5 cursor-pointer opacity-0 transition-opacity group-hover:opacity-100 data-[state=open]:opacity-100",
                          !pathname.startsWith(`/projects/${project.id}`) && "hover:bg-primary/10",
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
                      {editableOrganizationIds.has(organization.id) && (
                        <DropdownMenuItem asChild className="cursor-pointer">
                          <Link href={`/projects/${project.id}/settings`}>{t("settings")}</Link>
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              ))
            )}
          </div>
        ))}
      </nav>
      <div className="border-t p-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="w-full cursor-pointer justify-start truncate">
              {user?.email ?? tHeader("account")}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent side="top" align="start" className="w-52">
            <DropdownMenuItem disabled className="text-xs text-muted-foreground">
              {user?.email}
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem asChild>
              <Link href="/settings" className="flex cursor-pointer items-center gap-2">
                <Settings size={14} />
                {tHeader("userSettings")}
              </Link>
            </DropdownMenuItem>

            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="flex cursor-pointer items-center gap-2">
                <Languages size={14} />
                {tHeader("language")}
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                {LOCALES.map(({ value, label }) => (
                  <DropdownMenuItem
                    key={value}
                    onClick={() => handleLocaleSelect(value)}
                    className="flex cursor-pointer items-center gap-2"
                  >
                    <Check
                      size={14}
                      className={currentLocale === value ? "opacity-100" : "opacity-0"}
                    />
                    {label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuSubContent>
            </DropdownMenuSub>

            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="flex cursor-pointer items-center gap-2">
                <Sun size={14} />
                {tTheme("label")}
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                {THEMES.map(({ value, label, icon }) => (
                  <DropdownMenuItem
                    key={value}
                    onClick={() => handleThemeSelect(value)}
                    className="flex cursor-pointer items-center gap-2"
                  >
                    <Check
                      size={14}
                      className={theme === value ? "opacity-100" : "opacity-0"}
                    />
                    {icon}
                    {label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuSubContent>
            </DropdownMenuSub>

            <DropdownMenuSeparator />

            <DropdownMenuItem asChild>
              <a
                href="https://github.com/jbuget/raggae"
                target="_blank"
                rel="noreferrer"
                className="flex cursor-pointer items-center gap-2"
              >
                <Github size={14} />
                {t("sourceCode")}
              </a>
            </DropdownMenuItem>

            <DropdownMenuItem disabled className="text-xs text-muted-foreground">
              {gitBranch}@{shortCommit}
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem
              onClick={() => signOut({ callbackUrl: "/login" })}
              className="flex cursor-pointer items-center gap-2"
            >
              <LogOut size={14} />
              {tHeader("signOut")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  );
}
