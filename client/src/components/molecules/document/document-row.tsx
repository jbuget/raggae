"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Eye, Layers, RefreshCw, Trash2 } from "lucide-react";
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
import { DocumentChunksSheet } from "@/components/organisms/document/document-chunks-sheet";
import { getDocumentFileBlob } from "@/lib/api/documents";
import { useAuth } from "@/lib/hooks/use-auth";
import type {
  ChunkingStrategy,
  DocumentResponse,
  ProjectEmbeddingBackend,
} from "@/lib/types/api";
import { formatDate, formatDateTime, formatFileSize } from "@/lib/utils/format";

interface DocumentRowProps {
  document: DocumentResponse;
  embeddingBackend?: ProjectEmbeddingBackend | null;
  embeddingModel?: string | null;
  chunkingStrategy: ChunkingStrategy;
  parentChildChunking: boolean;
  onDelete: (id: string) => void;
  isDeleting: boolean;
  onReindex: (id: string) => void;
  reindexingId: string | null;
  disableReindex?: boolean;
}

export function DocumentRow({
  document,
  embeddingBackend,
  embeddingModel,
  chunkingStrategy,
  parentChildChunking,
  onDelete,
  isDeleting,
  onReindex,
  reindexingId,
  disableReindex = false,
}: DocumentRowProps) {
  const t = useTranslations("documents.row");
  const tStatus = useTranslations("documents.status");
  const tCommon = useTranslations("common");
  const { token } = useAuth();
  const isReindexing = reindexingId === document.id;
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [chunksOpen, setChunksOpen] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewType, setPreviewType] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const statusLabel = tStatus(document.status as "indexed" | "processing" | "uploaded" | "pending" | "error");
  const statusClassName =
    document.status === "indexed"
      ? "border-emerald-200 bg-emerald-100 text-emerald-800"
      : document.status === "processing"
        ? "border-sky-200 bg-sky-100 text-sky-800"
        : document.status === "uploaded"
          ? "border-amber-200 bg-amber-100 text-amber-800"
          : "border-red-200 bg-red-100 text-red-800";
  const embeddingBackendLabel = embeddingBackend ?? "default";
  const embeddingModelLabel = embeddingModel?.trim() ? embeddingModel : "default";
  const chunkingStrategyLabel = chunkingStrategy.replaceAll("_", " ");

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
      setPreviewError(t("unableToLoadPreview"));
    } finally {
      setPreviewLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-between rounded-md border p-4">
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium">{document.file_name}</p>
          <Badge
            variant="outline"
            className={`${statusClassName} px-1.5 py-0 text-[10px] leading-4`}
          >
            {statusLabel}
          </Badge>
          {document.status === "indexed" && document.last_indexed_at ? (
            <Badge variant="outline" className="px-1.5 py-0 text-[10px] leading-4">
              {t("indexedAt", { date: formatDateTime(document.last_indexed_at) })}
            </Badge>
          ) : null}
        </div>
        <div className="flex gap-3 text-xs text-muted-foreground">
          <span
            className="font-mono cursor-pointer hover:text-foreground"
            onClick={() => navigator.clipboard.writeText(document.id)}
            title={t("copyId")}
          >
            {document.id}
          </span>
          <span>{formatFileSize(document.file_size)}</span>
          <span>{formatDate(document.created_at)}</span>
          {document.status === "error" && document.error_message && (
            <span className="text-destructive">{document.error_message}</span>
          )}
        </div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
          <span>{t("indexDate")} {document.last_indexed_at ? formatDateTime(document.last_indexed_at) : "-"}</span>
          <span>{t("embedding")} {embeddingBackendLabel} / {embeddingModelLabel}</span>
          <span>{t("chunking")} {chunkingStrategyLabel}</span>
          <span>{t("parentChild")} {parentChildChunking ? tCommon("on") : tCommon("off")}</span>
        </div>
      </div>

      <div className="inline-flex overflow-hidden rounded-md border divide-x">
        <Button
          variant="ghost"
          size="icon-sm"
          className="cursor-pointer rounded-none border-0"
          onClick={handlePreviewOpen}
          aria-label={t("previewAriaLabel")}
          title={t("previewTitle")}
        >
          <Eye />
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          className="cursor-pointer rounded-none border-0"
          disabled={document.status !== "indexed"}
          onClick={() => setChunksOpen(true)}
          aria-label={t("chunksAriaLabel")}
          title={document.status === "indexed" ? t("chunksTitle") : t("chunksDisabledTitle")}
        >
          <Layers />
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          className="cursor-pointer rounded-none border-0"
          disabled={isReindexing || disableReindex}
          onClick={() => onReindex(document.id)}
          aria-label={isReindexing ? t("reindexingAriaLabel") : t("reindexAriaLabel")}
          title={isReindexing ? t("reindexingLabel") : t("reindexLabel")}
        >
          <RefreshCw className={isReindexing ? "animate-spin" : ""} />
        </Button>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            className="cursor-pointer rounded-none border-0 text-destructive"
            aria-label={t("deleteAriaLabel")}
            title={t("deleteTitle")}
          >
            <Trash2 />
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("deleteDocumentTitle")}</DialogTitle>
            <DialogDescription>
              {t("deleteConfirm", { name: document.file_name })}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" className="cursor-pointer" onClick={() => setDeleteOpen(false)}>
              {tCommon("cancel")}
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
              {isDeleting ? tCommon("deleting") : tCommon("delete")}
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
            {previewLoading && <p className="text-sm text-muted-foreground">{t("loadingPreview")}</p>}
            {!previewLoading && previewError && (
              <p className="text-sm text-destructive">{previewError}</p>
            )}
            {!previewLoading && !previewError && previewUrl && previewType === "application/pdf" && (
              <iframe src={previewUrl} title={document.file_name} className="h-[84vh] w-full rounded-md border" />
            )}
            {!previewLoading && !previewError && previewUrl && previewType?.startsWith("image/") && (
              <img src={previewUrl} alt={document.file_name} className="mx-auto max-h-[84vh] object-contain" />
            )}
            {!previewLoading && !previewError && previewUrl && previewType?.startsWith("text/") && (
              <iframe src={previewUrl} title={document.file_name} className="h-[84vh] w-full rounded-md border bg-background" />
            )}
            {!previewLoading &&
              !previewError &&
              previewUrl &&
              !previewType?.startsWith("image/") &&
              previewType !== "application/pdf" &&
              !previewType?.startsWith("text/") && (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    {t("previewNotAvailable")}
                  </p>
                  <a
                    href={previewUrl}
                    download={document.file_name}
                    className="inline-flex rounded-md border bg-background px-3 py-2 text-sm"
                  >
                    {t("downloadDocument")}
                  </a>
                </div>
              )}
          </div>
        </DialogContent>
      </Dialog>
      </div>

      <DocumentChunksSheet
        projectId={document.project_id}
        documentId={document.id}
        documentName={document.file_name}
        open={chunksOpen}
        onOpenChange={setChunksOpen}
      />
    </div>
  );
}
