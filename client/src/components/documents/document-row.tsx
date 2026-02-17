"use client";

import { useEffect, useState } from "react";
import { Eye, RefreshCw, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
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
import { getDocumentFileBlob } from "@/lib/api/documents";
import { useAuth } from "@/lib/hooks/use-auth";
import type { DocumentResponse } from "@/lib/types/api";
import { formatDate, formatFileSize } from "@/lib/utils/format";

interface DocumentRowProps {
  document: DocumentResponse;
  onDelete: (id: string) => void;
  isDeleting: boolean;
  onReindex: (id: string) => void;
  reindexingId: string | null;
  disableReindex?: boolean;
}

export function DocumentRow({
  document,
  onDelete,
  isDeleting,
  onReindex,
  reindexingId,
  disableReindex = false,
}: DocumentRowProps) {
  const { token } = useAuth();
  const isReindexing = reindexingId === document.id;
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewType, setPreviewType] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const statusLabel = document.status.charAt(0).toUpperCase() + document.status.slice(1);
  const statusClassName =
    document.status === "indexed"
      ? "border-emerald-200 bg-emerald-100 text-emerald-800"
      : document.status === "processing"
        ? "border-sky-200 bg-sky-100 text-sky-800"
        : document.status === "uploaded"
          ? "border-amber-200 bg-amber-100 text-amber-800"
          : "border-red-200 bg-red-100 text-red-800";

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  async function handlePreviewOpen() {
    if (!token) return;

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setPreviewType(null);
    setPreviewError(null);
    setPreviewLoading(true);
    setPreviewOpen(true);

    try {
      const blob = await getDocumentFileBlob(token, document.project_id, document.id);
      setPreviewUrl(URL.createObjectURL(blob));
      setPreviewType(blob.type || "application/octet-stream");
    } catch {
      setPreviewError("Unable to load preview for this document.");
    } finally {
      setPreviewLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-between rounded-md border p-4">
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium">{document.file_name}</p>
          <Badge variant="outline" className={statusClassName}>
            {statusLabel}
          </Badge>
        </div>
        <div className="flex gap-3 text-xs text-muted-foreground">
          <span
            className="font-mono cursor-pointer hover:text-foreground"
            onClick={() => navigator.clipboard.writeText(document.id)}
            title="Copy ID"
          >
            {document.id}
          </span>
          <span>{document.content_type}</span>
          <span>{formatFileSize(document.file_size)}</span>
          <span>{formatDate(document.created_at)}</span>
          {document.status === "error" && document.error_message && (
            <span className="text-destructive">{document.error_message}</span>
          )}
        </div>
      </div>

      <div className="flex gap-2">
        <Button
          variant="ghost"
          size="icon-sm"
          className="cursor-pointer"
          onClick={handlePreviewOpen}
          aria-label="Preview document"
          title="Preview"
        >
          <Eye />
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          className="cursor-pointer"
          disabled={isReindexing || disableReindex}
          onClick={() => onReindex(document.id)}
          aria-label={isReindexing ? "Reindexing document" : "Reindex document"}
          title={isReindexing ? "Reindexing..." : "Reindex"}
        >
          <RefreshCw className={isReindexing ? "animate-spin" : ""} />
        </Button>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            className="cursor-pointer text-destructive"
            aria-label="Delete document"
            title="Delete"
          >
            <Trash2 />
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &quot;{document.file_name}&quot;?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" className="cursor-pointer" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              className="cursor-pointer"
              disabled={isDeleting}
              onClick={() => {
                onDelete(document.id);
                setDeleteOpen(false);
              }}
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={previewOpen}
        onOpenChange={(open) => {
          setPreviewOpen(open);
          if (!open) {
            if (previewUrl) URL.revokeObjectURL(previewUrl);
            setPreviewUrl(null);
            setPreviewType(null);
            setPreviewError(null);
          }
        }}
      >
        <DialogContent className="h-[94vh] max-h-[94vh] w-[98vw] max-w-[98vw] overflow-hidden p-4 sm:max-w-none sm:p-6">
          <DialogHeader>
            <DialogTitle>{document.file_name}</DialogTitle>
          </DialogHeader>
          <div className="h-full min-h-0 overflow-y-auto rounded-md border bg-muted/20 p-3">
            {previewLoading && <p className="text-sm text-muted-foreground">Loading preview...</p>}
            {!previewLoading && previewError && (
              <p className="text-sm text-destructive">{previewError}</p>
            )}
            {!previewLoading && !previewError && previewUrl && previewType === "application/pdf" && (
              <iframe src={previewUrl} title={document.file_name} className="h-[84vh] w-full rounded-md border" />
            )}
            {!previewLoading && !previewError && previewUrl && previewType.startsWith("image/") && (
              <img src={previewUrl} alt={document.file_name} className="mx-auto max-h-[84vh] object-contain" />
            )}
            {!previewLoading && !previewError && previewUrl && previewType.startsWith("text/") && (
              <iframe src={previewUrl} title={document.file_name} className="h-[84vh] w-full rounded-md border bg-background" />
            )}
            {!previewLoading &&
              !previewError &&
              previewUrl &&
              !previewType.startsWith("image/") &&
              previewType !== "application/pdf" &&
              !previewType.startsWith("text/") && (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Preview is not available for this file type.
                  </p>
                  <a
                    href={previewUrl}
                    download={document.file_name}
                    className="inline-flex rounded-md border bg-background px-3 py-2 text-sm"
                  >
                    Download document
                  </a>
                </div>
              )}
          </div>
        </DialogContent>
      </Dialog>
      </div>
    </div>
  );
}
