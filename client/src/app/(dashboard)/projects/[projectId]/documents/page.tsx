"use client";

import { useParams } from "next/navigation";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";
import { DocumentRow } from "@/components/documents/document-row";
import { DocumentUpload } from "@/components/documents/document-upload";
import {
  useDeleteDocument,
  useDocuments,
  useReindexDocument,
  useUploadDocument,
} from "@/lib/hooks/use-documents";

export default function DocumentsPage() {
  const params = useParams<{ projectId: string }>();
  const { data: documents, isLoading } = useDocuments(params.projectId);
  const uploadDocument = useUploadDocument(params.projectId);
  const reindexDocument = useReindexDocument(params.projectId);
  const deleteDocument = useDeleteDocument(params.projectId);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Documents</h1>

      <DocumentUpload
        onUpload={(files) => {
          uploadDocument.mutate(files, {
            onSuccess: (result) =>
              toast.success(
                `${result.succeeded} uploaded, ${result.failed} failed`,
              ),
            onError: () => toast.error("Failed to upload document"),
          });
        }}
        isUploading={uploadDocument.isPending}
      />

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      ) : documents && documents.length === 0 ? (
        <p className="text-center py-8 text-muted-foreground">
          No documents yet. Upload your first document above.
        </p>
      ) : (
        <div className="space-y-3">
          {documents?.map((doc) => (
            <DocumentRow
              key={doc.id}
              document={doc}
              onReindex={(id) => {
                reindexDocument.mutate(id, {
                  onSuccess: () => toast.success("Document reindexed"),
                  onError: () => toast.error("Failed to reindex document"),
                });
              }}
              reindexingId={reindexDocument.isPending ? (reindexDocument.variables ?? null) : null}
              onDelete={(id) => {
                deleteDocument.mutate(id, {
                  onSuccess: () => toast.success("Document deleted"),
                  onError: () => toast.error("Failed to delete document"),
                });
              }}
              isDeleting={deleteDocument.isPending}
            />
          ))}
        </div>
      )}
    </div>
  );
}
