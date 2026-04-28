"use client";

import { useTranslations } from "next-intl";
import { ChunkAccordionItem } from "@/components/atoms/document/chunk-accordion-item";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useDocumentChunks } from "@/lib/hooks/use-documents";

interface DocumentChunksSheetProps {
  projectId: string;
  documentId: string;
  documentName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DocumentChunksSheet({
  projectId,
  documentId,
  documentName,
  open,
  onOpenChange,
}: DocumentChunksSheetProps) {
  const t = useTranslations("documents.chunks");
  const { data, isLoading, error } = useDocumentChunks(
    projectId,
    open ? documentId : null,
  );

  const chunks = data?.chunks ?? [];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex w-full flex-col sm:max-w-xl">
        <SheetHeader className="border-b pb-4">
          <SheetTitle className="truncate">{documentName}</SheetTitle>
          <SheetDescription>
            {!isLoading && !error ? t("title", { count: chunks.length }) : ""}
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto">
          {isLoading && (
            <p data-testid="chunks-loading" className="px-4 py-6 text-sm text-muted-foreground">
              {t("loading")}
            </p>
          )}
          {!isLoading && error && (
            <p data-testid="chunks-error" className="px-4 py-6 text-sm text-destructive">
              {t("error")}
            </p>
          )}
          {!isLoading && !error && chunks.length === 0 && (
            <p data-testid="chunks-empty" className="px-4 py-6 text-sm text-muted-foreground">
              {t("empty")}
            </p>
          )}
          {!isLoading && !error && chunks.length > 0 && (
            <div>
              {chunks.map((chunk) => (
                <ChunkAccordionItem
                  key={chunk.id}
                  chunk={chunk}
                  ariaLabel={t("chunkLabel", { index: chunk.chunk_index })}
                  metadataLabel={t("metadata")}
                />
              ))}
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
