"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Plus } from "lucide-react";
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
  const [createOrgId, setCreateOrgId] = useState<string | null>(null);
  const effectiveCreateOpen = createOpen || shouldOpenFromQuery;
  const effectiveOrgId = createOrgId ?? organizationIdFromQuery;
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>(getInitialViewMode);

  function handleViewChange(mode: ViewMode) {
    setViewMode(mode);
    localStorage.setItem(VIEW_MODE_STORAGE_KEY, mode);
  }

  function openCreateDialog(orgId: string | null = null) {
    setCreateOrgId(orgId);
    setCreateOpen(true);
  }

  function closeCreateDialog() {
    setCreateOpen(false);
    setCreateOrgId(null);
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
          </div>
          <DialogFooter>
            <Button
              onClick={() => {
                if (!name.trim()) return;
                createProject.mutate(
                  {
                    name: name.trim(),
                    description,
                    organization_id: effectiveOrgId,
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
              <h2 className="text-lg font-semibold mb-4">{t("list.myProjects")}</h2>
              <ProjectSection
                projects={personalProjects}
                viewMode={viewMode}
                showSettings={true}
              />
            </section>
          )}

          {nonEmptySections.map(({ organization, projects, canEdit }) => (
            <section key={organization.id}>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">{organization.name}</h2>
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
              <ProjectSection
                projects={projects}
                viewMode={viewMode}
                showSettings={canEdit}
              />
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
