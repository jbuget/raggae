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
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useProject, useReindexProject, useUpdateProject } from "@/lib/hooks/use-projects";
import type { ChunkingStrategy, UpdateProjectRequest } from "@/lib/types/api";

export function ProjectKnowledgeIndexingPanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");
  const tForm = useTranslations("projects.form");

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);
  const reindexProject = useReindexProject(projectId);

  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy | null>(null);
  const [parentChildChunking, setParentChildChunking] = useState<boolean | null>(null);
  const [reindexWarningOpen, setReindexWarningOpen] = useState(false);
  const [pendingData, setPendingData] = useState<UpdateProjectRequest | null>(null);

  if (!project) return null;

  const isProjectReindexing = project.reindex_status === "in_progress";
  const effectiveChunkingStrategy = chunkingStrategy ?? project.chunking_strategy;
  const effectiveParentChildChunking = parentChildChunking ?? project.parent_child_chunking;

  const hasChanges =
    effectiveChunkingStrategy !== project.chunking_strategy ||
    effectiveParentChildChunking !== project.parent_child_chunking;

  const isSemanticRecommended =
    effectiveParentChildChunking && effectiveChunkingStrategy !== "semantic";

  const payload: UpdateProjectRequest = {
    chunking_strategy: effectiveChunkingStrategy,
    parent_child_chunking: effectiveParentChildChunking,
  };

  function handleSave() {
    const parentChildChanged = effectiveParentChildChunking !== project?.parent_child_chunking;
    if (parentChildChanged) {
      setPendingData(payload);
      setReindexWarningOpen(true);
      return;
    }
    updateProject.mutate(payload, {
      onSuccess: () => toast.success(t("updateSuccess")),
      onError: () => toast.error(t("updateError")),
    });
  }

  return (
    <div className="max-w-3xl space-y-4 rounded-md">
      <p className="text-base font-semibold tracking-tight">{t("knowledgeIndexing.title")}</p>

      <div className="space-y-2">
        <Label htmlFor="chunkingStrategy">{t("knowledgeIndexing.chunkingLabel")}</Label>
        <select
          id="chunkingStrategy"
          value={effectiveChunkingStrategy}
          onChange={(e) => setChunkingStrategy(e.target.value as ChunkingStrategy)}
          className="border-input bg-background w-full rounded-md border px-3 py-2 text-sm"
        >
          <option value="auto">{tForm("chunkingAuto")}</option>
          <option value="fixed_window">{tForm("chunkingFixed")}</option>
          <option value="paragraph">{tForm("chunkingParagraph")}</option>
          <option value="heading_section">{tForm("chunkingHeading")}</option>
          <option value="semantic">{tForm("chunkingSemantic")}</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <Switch
          id="parentChildChunking"
          checked={effectiveParentChildChunking}
          onCheckedChange={setParentChildChunking}
        />
        <Label htmlFor="parentChildChunking">{t("knowledgeIndexing.parentChildLabel")}</Label>
      </div>
      <p className="text-xs text-muted-foreground">
        {t("knowledgeIndexing.parentChildRecommendation")}
      </p>
      {isSemanticRecommended && (
        <p className="text-xs text-amber-700">{t("knowledgeIndexing.parentChildWarning")}</p>
      )}

      <hr className="border-border" />

      <Button
        className="cursor-pointer"
        disabled={!hasChanges || updateProject.isPending}
        onClick={handleSave}
      >
        {updateProject.isPending ? tCommon("saving") : t("saveChanges")}
      </Button>

      <div className="space-y-3 rounded-md border p-4">
        <p className="text-base font-semibold tracking-tight">
          {t("knowledgeIndexing.reindexTitle")}
        </p>
        <p className="text-sm text-muted-foreground">
          {t("knowledgeIndexing.reindexDescription")}
        </p>
        <Button
          className="cursor-pointer"
          disabled={reindexProject.isPending || isProjectReindexing}
          onClick={() => {
            reindexProject.mutate(undefined, {
              onSuccess: (result) =>
                toast.success(
                  t("knowledgeIndexing.reindexSuccess", {
                    indexed: result.indexed_documents,
                    total: result.total_documents,
                    failed: result.failed_documents,
                  }),
                ),
              onError: () => toast.error(t("knowledgeIndexing.reindexError")),
            });
          }}
        >
          {reindexProject.isPending
            ? t("knowledgeIndexing.reindexing")
            : t("knowledgeIndexing.reindexButton")}
        </Button>
      </div>

      <Dialog open={reindexWarningOpen} onOpenChange={setReindexWarningOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{tForm("reindexTitle")}</DialogTitle>
            <DialogDescription>
              {tForm(
                effectiveParentChildChunking
                  ? "reindexEnableDescription"
                  : "reindexDisableDescription",
              )}{" "}
              {tForm("reindexDocumentsWarning")}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              className="cursor-pointer"
              onClick={() => {
                setReindexWarningOpen(false);
                setPendingData(null);
              }}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              className="cursor-pointer"
              onClick={() => {
                if (!pendingData) return;
                updateProject.mutate(pendingData, {
                  onSuccess: () => toast.success(t("updateSuccess")),
                  onError: () => toast.error(t("updateError")),
                });
                setReindexWarningOpen(false);
                setPendingData(null);
              }}
            >
              {tForm("confirmAndSave")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
