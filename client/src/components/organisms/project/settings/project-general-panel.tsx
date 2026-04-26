"use client";

import { useState } from "react";
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
import {
  useProject,
  usePublishProject,
  useUnpublishProject,
  useUpdateProject,
} from "@/lib/hooks/use-projects";

export function ProjectGeneralPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);
  const publishProject = usePublishProject(projectId);
  const unpublishProject = useUnpublishProject(projectId);

  const [name, setName] = useState<string | null>(null);
  const [description, setDescription] = useState<string | null>(null);
  const [publishOpen, setPublishOpen] = useState(false);
  const [unpublishOpen, setUnpublishOpen] = useState(false);

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
    <div className="max-w-3xl space-y-8">
      {/* Identity */}
      <div className="space-y-6">
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
        <Button className="cursor-pointer" disabled={isDisabled} onClick={handleSave}>
          {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
        </Button>
      </div>

      <hr className="border-border" />

      {/* Access */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold tracking-tight">{t("publication.accessTitle")}</h2>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">{t("publication.statusLabel")}</span>
          {project.is_published ? (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
              <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
              {t("publication.published")}
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
              <span className="h-1.5 w-1.5 rounded-full bg-gray-400" />
              {t("publication.unpublished")}
            </span>
          )}
        </div>

        {project.is_published && (
          <div className="space-y-2">
            <p className="text-sm font-medium">{t("publication.publicUrl")}</p>
            <div className="flex items-center gap-2 rounded-md border bg-muted/40 px-3 py-2">
              <code className="flex-1 truncate text-xs text-muted-foreground">
                {typeof window !== "undefined" ? window.location.origin : ""}/chat/{project.id}
              </code>
              <Button
                type="button"
                variant="outline"
                className="h-7 cursor-pointer px-2 text-xs"
                onClick={() => {
                  navigator.clipboard.writeText(`${window.location.origin}/chat/${project.id}`);
                  toast.success(t("publication.urlCopied"));
                }}
              >
                {t("publication.copy")}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">{t("publication.noteNotAvailable")}</p>
          </div>
        )}

        {project.is_published ? (
          <Dialog open={unpublishOpen} onOpenChange={setUnpublishOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="cursor-pointer">
                {t("publication.unpublishButton")}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t("publication.unpublishDialogTitle")}</DialogTitle>
                <DialogDescription>{t("publication.unpublishDialogDescription")}</DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" className="cursor-pointer" onClick={() => setUnpublishOpen(false)}>
                  {tCommon("cancel")}
                </Button>
                <Button className="cursor-pointer" disabled={unpublishProject.isPending}
                  onClick={() => unpublishProject.mutate(undefined, {
                    onSuccess: () => { toast.success(t("publication.unpublishSuccess")); setUnpublishOpen(false); },
                    onError: () => toast.error(t("publication.unpublishError")),
                  })}
                >
                  {unpublishProject.isPending ? t("publication.unpublishing") : tCommon("confirm")}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        ) : (
          <Dialog open={publishOpen} onOpenChange={setPublishOpen}>
            <DialogTrigger asChild>
              <Button className="cursor-pointer">{t("publication.publishButton")}</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t("publication.publishDialogTitle")}</DialogTitle>
                <DialogDescription>{t("publication.publishDialogDescription")}</DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" className="cursor-pointer" onClick={() => setPublishOpen(false)}>
                  {tCommon("cancel")}
                </Button>
                <Button className="cursor-pointer" disabled={publishProject.isPending}
                  onClick={() => publishProject.mutate(undefined, {
                    onSuccess: () => { toast.success(t("publication.publishSuccess")); setPublishOpen(false); },
                    onError: () => toast.error(t("publication.publishError")),
                  })}
                >
                  {publishProject.isPending ? t("publication.publishing") : tCommon("confirm")}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </div>
  );
}
