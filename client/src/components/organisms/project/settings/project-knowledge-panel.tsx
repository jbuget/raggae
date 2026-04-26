"use client";

import { toast } from "sonner";
import { useTranslations } from "next-intl";
import { Skeleton } from "@/components/ui/skeleton";
import { DocumentRow } from "@/components/molecules/document/document-row";
import { DocumentUpload } from "@/components/molecules/document/document-upload";
import { useProject } from "@/lib/hooks/use-projects";
import {
  useDeleteDocument,
  useDocuments,
  useReindexDocument,
  useUploadDocument,
} from "@/lib/hooks/use-documents";

export function ProjectKnowledgePanel({ projectId }: { projectId: string }) {
  const t = useTranslations("projects.settings");

  const { data: project } = useProject(projectId);
  const { data: documents, isLoading: isDocumentsLoading } = useDocuments(projectId);
  const uploadDocument = useUploadDocument(projectId);
  const reindexDocument = useReindexDocument(projectId);
  const deleteDocument = useDeleteDocument(projectId);

  if (!project) return null;

  const isProjectReindexing = project.reindex_status === "in_progress";
  const indexedCount = documents?.filter((doc) => doc.status === "indexed").length ?? 0;
  const totalCount = documents?.length ?? 0;

  return (
    <div className="max-w-4xl space-y-4">
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
        <p className="text-sm text-muted-foreground">{t("documentIngestion.empty")}</p>
      )}
    </div>
  );
}
