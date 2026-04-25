"use client";

import { useCallback, useRef, useState } from "react";
import { Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { formatFileSize } from "@/lib/utils/format";

const SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"] as const;
const ACCEPT = SUPPORTED_EXTENSIONS.join(",");

function isSupportedFile(file: File): boolean {
  const name = file.name.toLowerCase();
  return SUPPORTED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

interface DocumentUploadProps {
  onUpload: (files: File[]) => void;
  isUploading: boolean;
  uploadProgress?: number;
  disabled?: boolean;
}

export function DocumentUpload({ onUpload, isUploading, uploadProgress = 0, disabled = false }: DocumentUploadProps) {
  const t = useTranslations("documents.upload");
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFiles = useCallback((files: File[], toastFn: typeof toast) => {
    const rejected = files.filter((f) => !isSupportedFile(f));
    const accepted = files.filter(isSupportedFile);

    for (const file of rejected) {
      const ext = file.name.includes(".") ? `.${file.name.split(".").pop()}` : t("unknownExtension");
      toastFn.error(t("unsupportedFormat", { ext }));
    }

    if (accepted.length === 0) return;

    setSelectedFiles((previous) => {
      const merged = [...previous, ...accepted];
      const uniqueByName = new Map<string, File>();
      for (const file of merged) {
        uniqueByName.set(file.name, file);
      }
      return Array.from(uniqueByName.values());
    });
  }, [t]);

  function handleDrop(e: React.DragEvent) {
    if (disabled) return;
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) handleFiles(files, toast);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (disabled) return;
    const files = Array.from(e.target.files ?? []);
    if (files.length > 0) handleFiles(files, toast);
  }

  function handleUpload() {
    if (disabled) return;
    if (selectedFiles.length > 0) {
      onUpload(selectedFiles);
      setSelectedFiles([]);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div
          className={`flex flex-col items-center gap-4 rounded-lg border-2 border-dashed p-8 transition-colors ${
            isDragOver
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25"
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          data-testid="drop-zone"
        >
          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              {t("dragAndDrop")}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {t("supportedFormats", { formats: SUPPORTED_EXTENSIONS.join(", ") })}
            </p>
          </div>
          <input
            ref={inputRef}
            type="file"
            multiple
            accept={ACCEPT}
            onChange={handleChange}
            className="hidden"
            aria-label={t("selectFiles")}
          />
          <Button
            type="button"
            variant="outline"
            className="cursor-pointer"
            onClick={() => inputRef.current?.click()}
            disabled={disabled}
          >
            {t("selectFiles")}
          </Button>
        </div>

        {isUploading && (
          <div className="mt-4 space-y-1">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{uploadProgress >= 95 ? t("processing") : t("uploading")}</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {selectedFiles.length > 0 && (
          <div className="mt-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium">
                {selectedFiles.length} {t("filesSelected")}
              </p>
              <p className="text-xs text-muted-foreground">
                {selectedFiles.map((file) => file.name).join(", ")}
              </p>
              <p className="text-xs text-muted-foreground">
                {formatFileSize(
                  selectedFiles.reduce((total, file) => total + file.size, 0),
                )}
              </p>
            </div>
            <Button
              className="cursor-pointer"
              onClick={handleUpload}
              disabled={isUploading || disabled}
            >
              {isUploading && <Loader2 className="animate-spin" />}
              {isUploading ? t("uploading") : t("upload")}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
