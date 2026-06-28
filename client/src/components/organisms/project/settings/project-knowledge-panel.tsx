"use client";

import { FileText } from "lucide-react";
import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { InlineAlert } from "@/components/atoms/feedback/inline-alert";
import { Skeleton } from "@/components/ui/skeleton";
import { DocumentRow } from "@/components/molecules/document/document-row";
import { DocumentUpload } from "@/components/molecules/document/document-upload";
import { useProject, useProjectConfiguration } from "@/lib/hooks/use-projects";
import { useUserProjectDefaults } from "@/lib/hooks/use-user-project-defaults";
import { useOrganizationProjectDefaults } from "@/lib/hooks/use-org-project-defaults";
import { useSystemDefaults } from "@/lib/hooks/use-system-defaults";
import type { ChunkingStrategy, ProjectEmbeddingBackend } from "@/lib/types/api";
import {
  useDeleteDocument,
  useDocuments,
  useReindexDocument,
  useUploadDocument,
} from "@/lib/hooks/use-documents";

export function ProjectKnowledgePanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");

  const { data: project } = useProject(projectId);
  const { data: projectConfig } = useProjectConfiguration(projectId);
  const { data: userDefaults } = useUserProjectDefaults();
  const { data: orgDefaults } = useOrganizationProjectDefaults(project?.organization_id);
  const { data: systemDefaults } = useSystemDefaults();
  const { data: documents, isLoading: isDocumentsLoading } = useDocuments(projectId);
  const uploadDocument = useUploadDocument(projectId);
  const reindexDocument = useReindexDocument(projectId);
  const deleteDocument = useDeleteDocument(projectId);

  if (!project) return null;

  const isProjectReindexing = project.reindex_status === "in_progress";
  const indexedCount = documents?.filter((doc) => doc.status === "indexed").length ?? 0;
  const totalCount = documents?.length ?? 0;

  const inheritedDefaults = project.organization_id ? orgDefaults : userDefaults;
  const effectiveEmbeddingBackend =
    projectConfig?.embedding_backend ??
    inheritedDefaults?.embedding_backend ??
    systemDefaults?.embedding_backend;
  const hasEmbeddingModel = !!effectiveEmbeddingBackend;

  return (
    <div className="space-y-4">
      {!hasEmbeddingModel && (
        <InlineAlert>{t("documentIngestion.noEmbeddingModel")}</InlineAlert>
      )}
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
              embeddingBackend={(projectConfig?.embedding_backend ?? null) as ProjectEmbeddingBackend | null}
              embeddingModel={projectConfig?.embedding_model ?? null}
              chunkingStrategy={(projectConfig?.chunking_strategy ?? "auto") as ChunkingStrategy}
              parentChildChunking={projectConfig?.parent_child_chunking ?? false}
              onReindex={(id) => {
                if (isProjectReindexing) return;
                reindexDocument.mutate(id, {
                  onSuccess: () => toast.success(t("documentIngestion.reindexSuccess")),
                  onError: () => toast.error(t("documentIngestion.reindexError")),
                });
              }}
              reindexingId={reindexDocument.isPending ? (reindexDocument.variables ?? null) : null}
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
        <div className="flex flex-col items-center justify-center gap-2 rounded-md border border-dashed py-10 px-4 text-center">
          <FileText className="size-8 text-muted-foreground/60" aria-hidden="true" />
          <p className="text-sm text-muted-foreground">{t("documentIngestion.empty")}</p>
        </div>
      )}


    </div>
  );
}
