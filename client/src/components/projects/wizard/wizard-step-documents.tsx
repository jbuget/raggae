"use client";

import { useCallback, useRef } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { formatFileSize } from "@/lib/utils/format";

interface WizardStepDocumentsProps {
  files: File[];
  onFilesChange: (updater: (prev: File[]) => File[]) => void;
  onSubmit: () => void;
  onBack: () => void;
  isSubmitting: boolean;
}

export function WizardStepDocuments({
  files,
  onFilesChange,
  onSubmit,
  onBack,
  isSubmitting,
}: WizardStepDocumentsProps) {
  const t = useTranslations("projects.wizard");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    (newFiles: File[]) => {
      onFilesChange((prev: File[]) => {
        const merged = [...prev, ...newFiles];
        const unique = new Map<string, File>();
        for (const f of merged) unique.set(f.name, f);
        return Array.from(unique.values());
      });
    },
    [onFilesChange],
  );

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = Array.from(e.target.files ?? []);
    if (selected.length > 0) handleFiles(selected);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files);
    if (dropped.length > 0) handleFiles(dropped);
  }

  function removeFile(name: string) {
    onFilesChange((prev: File[]) => prev.filter((f) => f.name !== name));
  }

  const totalSize = files.reduce((sum, f) => sum + f.size, 0);

  return (
    <div className="space-y-4">
      <div
        className="flex flex-col items-center gap-3 rounded-lg border-2 border-dashed border-muted-foreground/25 p-8 transition-colors hover:border-muted-foreground/50"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <p className="text-sm text-muted-foreground">{t("dropZoneLabel")}</p>
        <input
          ref={inputRef}
          type="file"
          multiple
          onChange={handleChange}
          className="hidden"
          accept=".txt,.md,.pdf,.docx,.doc"
        />
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => inputRef.current?.click()}
          disabled={isSubmitting}
        >
          {t("selectFiles")}
        </Button>
        <p className="text-xs text-muted-foreground">{t("acceptedFormats")}</p>
      </div>

      {files.length > 0 && (
        <ul className="space-y-1">
          {files.map((file) => (
            <li key={file.name} className="flex items-center justify-between text-sm">
              <span className="truncate text-muted-foreground">
                {file.name}{" "}
                <span className="text-xs">({formatFileSize(file.size)})</span>
              </span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs"
                onClick={() => removeFile(file.name)}
                disabled={isSubmitting}
              >
                ×
              </Button>
            </li>
          ))}
          <li className="text-xs text-muted-foreground pt-1">
            {files.length} {t("filesSelected")} — {formatFileSize(totalSize)}
          </li>
        </ul>
      )}

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack} disabled={isSubmitting}>
          {t("back")}
        </Button>
        <div className="flex gap-2">
          {files.length === 0 && (
            <Button variant="outline" onClick={onSubmit} disabled={isSubmitting}>
              {isSubmitting ? t("creating") : t("skipAndCreate")}
            </Button>
          )}
          {files.length > 0 && (
            <Button onClick={onSubmit} disabled={isSubmitting}>
              {isSubmitting ? t("creating") : t("createWithDocuments", { count: files.length })}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
