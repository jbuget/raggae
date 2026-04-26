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
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { DocumentRow } from "@/components/molecules/document/document-row";
import { DocumentUpload } from "@/components/molecules/document/document-upload";
import { useProject, useReindexProject, useUpdateProject } from "@/lib/hooks/use-projects";
import {
  useDeleteDocument,
  useDocuments,
  useReindexDocument,
  useUploadDocument,
} from "@/lib/hooks/use-documents";
import type { ChunkingStrategy, UpdateProjectRequest } from "@/lib/types/api";

export function ProjectKnowledgePanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");
  const tCommon = useTranslations("common");
  const tForm = useTranslations("projects.form");

  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject(projectId);
  const reindexProject = useReindexProject(projectId);
  const { data: documents, isLoading: isDocumentsLoading } = useDocuments(projectId);
  const uploadDocument = useUploadDocument(projectId);
  const reindexDocument = useReindexDocument(projectId);
  const deleteDocument = useDeleteDocument(projectId);

  const [chunkingStrategy, setChunkingStrategy] = useState<ChunkingStrategy | null>(null);
  const [parentChildChunking, setParentChildChunking] = useState<boolean | null>(null);
  const [reindexWarningOpen, setReindexWarningOpen] = useState(false);
  const [pendingData, setPendingData] = useState<UpdateProjectRequest | null>(null);

  if (!project) return null;

  const isProjectReindexing = project.reindex_status === "in_progress";
  const indexedCount = documents?.filter((doc) => doc.status === "indexed").length ?? 0;
  const totalCount = documents?.length ?? 0;

  const effectiveChunkingStrategy = chunkingStrategy ?? project.chunking_strategy;
  const effectiveParentChildChunking = parentChildChunking ?? project.parent_child_chunking;

  const hasIndexingChanges =
    effectiveChunkingStrategy !== project.chunking_strategy ||
    effectiveParentChildChunking !== project.parent_child_chunking;

  const isSemanticRecommended =
    effectiveParentChildChunking && effectiveChunkingStrategy !== "semantic";

  const indexingPayload: UpdateProjectRequest = {
    chunking_strategy: effectiveChunkingStrategy,
    parent_child_chunking: effectiveParentChildChunking,
  };

  function handleIndexingSave() {
    const parentChildChanged = effectiveParentChildChunking !== project?.parent_child_chunking;
    if (parentChildChanged) {
      setPendingData(indexingPayload);
      setReindexWarningOpen(true);
      return;
    }
    updateProject.mutate(indexingPayload, {
      onSuccess: () => toast.success(t("updateSuccess")),
      onError: () => toast.error(t("updateError")),
    });
  }

  return (
    <div className="max-w-4xl space-y-10">
      {/* Documents */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold tracking-tight">
          {t("documentIngestion.title")}
        </h2>
        <p className="text-sm text-muted-foreground">{t("documentIngestion.description")}</p>
        <p className="text-sm text-muted-foreground">
          {t("documentIngestion.indexedTotal", { indexed: indexedCount, total: totalCount })}
        </p>
        <DocumentUpload
          isUploading={uploadDocument.isPending}
          uploadProgress={uploadDocument.progress}
          onUpload={(files) => {
            uploadDocument.mutate(files, {
              onSuccess: (result) =>
                toast.success(
                  t("documentIngestion.uploadSuccess", {
                    succeeded: result.succeeded,
                    failed: result.failed,
                  }),
                ),
              onError: () => toast.error(t("documentIngestion.uploadError")),
            });
          }}
          disabled={isProjectReindexing}
        />
        {isDocumentsLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 2 }).map((_, i) => (
              <Skeleton key={i} className="h-16" />
            ))}
          </div>
        ) : documents && documents.length > 0 ? (
          <div className="space-y-3">
            {documents.map((doc) => (
              <DocumentRow
                key={doc.id}
                document={doc}
                embeddingBackend={project.embedding_backend}
                embeddingModel={project.embedding_model}
                chunkingStrategy={project.chunking_strategy}
                parentChildChunking={project.parent_child_chunking}
                onReindex={(id) => {
                  if (isProjectReindexing) return;
                  reindexDocument.mutate(id, {
                    onSuccess: () => toast.success(t("documentIngestion.reindexSuccess")),
                    onError: () => toast.error(t("documentIngestion.reindexError")),
                  });
                }}
                reindexingId={
                  reindexDocument.isPending ? (reindexDocument.variables ?? null) : null
                }
                disableReindex={isProjectReindexing}
                onDelete={(id) => {
                  deleteDocument.mutate(id, {
                    onSuccess: () => toast.success(t("documentIngestion.deleteSuccess")),
                    onError: () => toast.error(t("documentIngestion.deleteError")),
                  });
                }}
                isDeleting={deleteDocument.isPending}
              />
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">{t("documentIngestion.empty")}</p>
        )}
      </div>

      <hr className="border-border" />

      {/* Indexation */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold tracking-tight">
          {t("knowledgeIndexing.title")}
        </h2>

        {isProjectReindexing && (
          <div className="rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {t("reindexingWarning", {
              progress: project.reindex_progress,
              total: project.reindex_total,
            })}
          </div>
        )}

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

        <Button
          className="cursor-pointer"
          disabled={!hasIndexingChanges || updateProject.isPending}
          onClick={handleIndexingSave}
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
