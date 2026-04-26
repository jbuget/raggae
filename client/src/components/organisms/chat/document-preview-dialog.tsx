"use client";

import { useTranslations } from "next-intl";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface MessageSourceDocument {
  documentId: string;
  documentName: string;
  chunkIds: string[];
}

interface DocumentPreviewDialogProps {
  source: MessageSourceDocument | null;
  documentUrl: string | null;
  documentType: string | null;
  isLoading: boolean;
  error: string | null;
  onClose: () => void;
}

export function DocumentPreviewDialog({
  source,
  documentUrl,
  documentType,
  isLoading,
  error,
  onClose,
}: DocumentPreviewDialogProps) {
  const t = useTranslations("chat.panel");

  return (
    <Dialog
      open={source !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent className="h-[94vh] max-h-[94vh] w-[98vw] max-w-[98vw] sm:max-w-none overflow-hidden p-4 sm:p-6">
        <DialogHeader>
          <DialogTitle>{source?.documentName || t("documentPreview")}</DialogTitle>
          {source?.chunkIds && source.chunkIds.length > 0 && (
            <div className="mt-1 space-y-1">
              {source.chunkIds.map((chunkId) => (
                <div key={chunkId} className="flex items-center gap-2 text-xs text-muted-foreground">
                  <code className="rounded bg-muted px-1.5 py-0.5 font-mono">{chunkId}</code>
                  <button
                    type="button"
                    className="rounded px-1.5 py-0.5 text-xs hover:bg-muted"
                    onClick={() => navigator.clipboard.writeText(chunkId)}
                    title={t("copyChunkIdTitle")}
                  >
                    {t("copyChunkId")}
                  </button>
                </div>
              ))}
            </div>
          )}
        </DialogHeader>
        <div className="h-full min-h-0 overflow-y-auto rounded-md border bg-muted/20 p-3">
          {isLoading && (
            <p className="text-sm text-muted-foreground">{t("loadingDocument")}</p>
          )}
          {!isLoading && error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
          {!isLoading && !error && documentUrl && documentType?.startsWith("image/") && (
            <img
              src={documentUrl}
              alt={source?.documentName || "Document"}
              className="mx-auto max-h-[84vh] object-contain"
            />
          )}
          {!isLoading && !error && documentUrl && documentType === "application/pdf" && (
            <iframe
              src={documentUrl}
              title={source?.documentName || "Document"}
              className="h-[84vh] w-full rounded-md border"
            />
          )}
          {!isLoading && !error && documentUrl && documentType?.startsWith("text/") && (
            <iframe
              src={documentUrl}
              title={source?.documentName || "Document"}
              className="h-[84vh] w-full rounded-md border bg-background"
            />
          )}
          {!isLoading && !error && documentUrl &&
            !documentType?.startsWith("image/") &&
            documentType !== "application/pdf" &&
            !documentType?.startsWith("text/") && (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">{t("previewNotAvailable")}</p>
                <a
                  href={documentUrl}
                  download={source?.documentName}
                  className="inline-flex rounded-md border bg-background px-3 py-2 text-sm"
                >
                  {t("downloadDocument")}
                </a>
              </div>
            )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
