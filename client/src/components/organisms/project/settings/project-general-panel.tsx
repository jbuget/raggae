"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useDeleteProject, useProject, useUpdateProject } from "@/lib/hooks/use-projects";

export function ProjectGeneralPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");
  const router = useRouter();

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);
  const deleteProject = useDeleteProject();

  const [name, setName] = useState<string | null>(null);
  const [description, setDescription] = useState<string | null>(null);
  const [deleteOpen, setDeleteOpen] = useState(false);

  if (!project) return null;

  const effectiveName = name ?? project.name;
  const effectiveDescription = description ?? (project.description ?? "");

  const hasChanges =
    effectiveName !== project.name ||
    effectiveDescription !== (project.description ?? "");

  const isDisabled = !effectiveName.trim() || updateProject.isPending || !hasChanges;

  function handleSave() {
    updateProject.mutate(
      { name: effectiveName.trim(), description: effectiveDescription },
      {
        onSuccess: () => toast.success(t("updateSuccess")),
        onError: () => toast.error(t("updateError")),
      },
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="space-y-6 rounded-md">
        <div className="space-y-2">
          <Label htmlFor="name">{t("general.nameLabel")}</Label>
          <Input
            id="name"
            value={effectiveName}
            onChange={(e) => setName(e.target.value)}
            placeholder={t("general.namePlaceholder")}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="description">{t("general.descriptionLabel")}</Label>
          <Textarea
            id="description"
            value={effectiveDescription}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={t("general.descriptionPlaceholder")}
            rows={3}
          />
        </div>
      </div>

      <Button className="cursor-pointer" disabled={isDisabled} onClick={handleSave}>
        {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
      </Button>

      <div className="space-y-3 rounded-md border p-4">
        <p className="text-base font-semibold tracking-tight">{t("general.deleteTitle")}</p>
        <p className="text-sm text-muted-foreground">{t("general.deleteDescription")}</p>
        <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
          <DialogTrigger asChild>
            <Button variant="destructive" className="cursor-pointer">
              {t("general.deleteButton")}
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t("general.deleteDialogTitle")}</DialogTitle>
              <DialogDescription>
                {t("general.deleteDialogDescription", { name: project.name })}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                className="cursor-pointer"
                onClick={() => setDeleteOpen(false)}
              >
                {tCommon("cancel")}
              </Button>
              <Button
                variant="destructive"
                className="cursor-pointer"
                disabled={deleteProject.isPending}
                onClick={() => {
                  deleteProject.mutate(project.id, {
                    onSuccess: () => {
                      toast.success(t("general.deleteSuccess"));
                      router.push("/projects");
                    },
                    onError: () => toast.error(t("general.deleteError")),
                  });
                }}
              >
                {deleteProject.isPending ? tCommon("deleting") : tCommon("delete")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
