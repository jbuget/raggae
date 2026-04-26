"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { ProjectCard } from "@/components/molecules/project/project-card";
import { useCreateProject, useProjects } from "@/lib/hooks/use-projects";

export function ProjectList() {
  const t = useTranslations("projects");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const searchParams = useSearchParams();
  const { data: projects, isLoading, error } = useProjects();
  const createProject = useCreateProject();
  const shouldOpenFromQuery = searchParams.get("create") === "1";
  const organizationIdFromQuery = searchParams.get("organizationId");
  const [createOpen, setCreateOpen] = useState(false);
  const effectiveCreateOpen = createOpen || shouldOpenFromQuery;
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-destructive">
        Failed to load projects
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("title")}</h1>
        <Dialog
          open={effectiveCreateOpen}
          onOpenChange={(open) => {
            setCreateOpen(open);
            if (!open && shouldOpenFromQuery) {
              router.replace("/projects");
            }
          }}
        >
          <DialogTrigger asChild>
            <Button>{t("new")}</Button>
          </DialogTrigger>
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
                      organization_id: organizationIdFromQuery || null,
                    },
                    {
                      onSuccess: (project) => {
                        toast.success(t("list.createSuccess"));
                        setCreateOpen(false);
                        setName("");
                        setDescription("");
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
      </div>

      {projects && projects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">{t("empty")}</p>
          <Button onClick={() => setCreateOpen(true)}>{t("list.createFirst")}</Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects?.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  );
}
