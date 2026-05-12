"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ChevronDown, ChevronRight, Plus } from "lucide-react";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { ViewToggle, type ViewMode } from "@/components/atoms/layout/view-toggle";
import { ProjectCard } from "@/components/molecules/project/project-card";
import { ProjectListItem } from "@/components/molecules/project/project-list-item";
import { useAccessibleProjects } from "@/lib/hooks/use-accessible-projects";
import { useCreateProject } from "@/lib/hooks/use-projects";
import type { ProjectResponse } from "@/lib/types/api";

const VIEW_MODE_STORAGE_KEY = "projects-view-mode";

function getInitialViewMode(): ViewMode {
  if (typeof window === "undefined") return "grid";
  return (localStorage.getItem(VIEW_MODE_STORAGE_KEY) as ViewMode) ?? "grid";
}

function ProjectSection({
  projects,
  viewMode,
  showSettings,
}: {
  projects: ProjectResponse[];
  viewMode: ViewMode;
  showSettings: boolean;
}) {
  if (viewMode === "grid") {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <ProjectCard key={project.id} project={project} showSettings={showSettings} />
        ))}
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-2">
      {projects.map((project) => (
        <ProjectListItem key={project.id} project={project} showSettings={showSettings} />
      ))}
    </div>
  );
}

export function ProjectList() {
  const t = useTranslations("projects");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const searchParams = useSearchParams();
  const { personalProjects, organizationSections, isLoading, error } = useAccessibleProjects();
  const createProject = useCreateProject();
  const shouldOpenFromQuery = searchParams.get("create") === "1";
  const organizationIdFromQuery = searchParams.get("organizationId");
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedOrgId, setSelectedOrgId] = useState<string | null>(null);
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());
  const effectiveCreateOpen = createOpen || shouldOpenFromQuery;
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>(getInitialViewMode);

  function handleViewChange(mode: ViewMode) {
    setViewMode(mode);
    localStorage.setItem(VIEW_MODE_STORAGE_KEY, mode);
  }

  function toggleSection(id: string) {
    setCollapsedSections((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }

  function openCreateDialog(orgId: string | null = null) {
    setSelectedOrgId(orgId ?? organizationIdFromQuery);
    setCreateOpen(true);
  }

  function closeCreateDialog() {
    setCreateOpen(false);
    setSelectedOrgId(null);
    setName("");
    setDescription("");
    if (shouldOpenFromQuery) {
      router.replace("/projects");
    }
  }

  if (error) {
    return <p className="text-destructive">{t("loadError")}</p>;
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  const nonEmptySections = organizationSections.filter((s) => s.projects.length > 0);
  const isEmpty = personalProjects.length === 0 && nonEmptySections.length === 0;

  return (
    <div className="space-y-6">
      <Dialog
        open={effectiveCreateOpen}
        onOpenChange={(open) => {
          if (!open) closeCreateDialog();
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("list.createTitle")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="new-project-name">{t("form.nameLabel")}</Label>
              <Input
                id="new-project-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={t("form.namePlaceholder")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-project-description">Description</Label>
              <Textarea
                id="new-project-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What is this project about?"
                rows={3}
              />
            </div>
            {organizationSections.some((s) => s.canEdit) && (
              <div className="space-y-2">
                <Label htmlFor="new-project-org">{t("list.createIn")}</Label>
                <Select
                  value={selectedOrgId ?? "personal"}
                  onValueChange={(val) => setSelectedOrgId(val === "personal" ? null : val)}
                >
                  <SelectTrigger id="new-project-org">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="personal">{t("list.createInPersonal")}</SelectItem>
                    {organizationSections
                      .filter((s) => s.canEdit)
                      .map((s) => (
                        <SelectItem key={s.organization.id} value={s.organization.id}>
                          {s.organization.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button
              onClick={() => {
                if (!name.trim()) return;
                createProject.mutate(
                  {
                    name: name.trim(),
                    description,
                    organization_id: selectedOrgId,
                  },
                  {
                    onSuccess: (project) => {
                      toast.success(t("list.createSuccess"));
                      closeCreateDialog();
                      router.push(`/projects/${project.id}/settings`);
                    },
                    onError: () => toast.error(t("list.createError")),
                  },
                );
              }}
              disabled={!name.trim() || createProject.isPending}
            >
              {createProject.isPending ? tCommon("creating") : t("list.createTitle")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {!isEmpty && (
        <div className="flex justify-end">
          <ViewToggle
            value={viewMode}
            onChange={handleViewChange}
            gridLabel={t("list.gridView")}
            listLabel={t("list.listView")}
          />
        </div>
      )}

      {isEmpty ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">{t("empty")}</p>
          <Button onClick={() => openCreateDialog()}>{t("list.createFirst")}</Button>
        </div>
      ) : (
        <div className="space-y-8">
          {personalProjects.length > 0 && (
            <section>
              <div className="flex items-center justify-between mb-4">
                <button
                  type="button"
                  className="flex items-center gap-1.5 text-lg font-semibold hover:text-muted-foreground transition-colors"
                  onClick={() => toggleSection("personal")}
                >
                  {collapsedSections.has("personal")
                    ? <ChevronRight className="size-4" />
                    : <ChevronDown className="size-4" />}
                  {t("list.myProjects")}
                </button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => openCreateDialog(null)}
                >
                  <Plus className="mr-1 size-4" />
                  {t("new")}
                </Button>
              </div>
              {!collapsedSections.has("personal") && (
                <ProjectSection
                  projects={personalProjects}
                  viewMode={viewMode}
                  showSettings={true}
                />
              )}
            </section>
          )}

          {nonEmptySections.map(({ organization, projects, canEdit }) => (
            <section key={organization.id}>
              <div className="flex items-center justify-between mb-4">
                <button
                  type="button"
                  className="flex items-center gap-1.5 text-lg font-semibold hover:text-muted-foreground transition-colors"
                  onClick={() => toggleSection(organization.id)}
                >
                  {collapsedSections.has(organization.id)
                    ? <ChevronRight className="size-4" />
                    : <ChevronDown className="size-4" />}
                  {organization.name}
                </button>
                {canEdit && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openCreateDialog(organization.id)}
                  >
                    <Plus className="mr-1 size-4" />
                    {t("new")}
                  </Button>
                )}
              </div>
              {!collapsedSections.has(organization.id) && (
                <ProjectSection
                  projects={projects}
                  viewMode={viewMode}
                  showSettings={canEdit}
                />
              )}
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
