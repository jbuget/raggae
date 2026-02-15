"use client";

import { useCallback, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { formatFileSize } from "@/lib/utils/format";

interface DocumentUploadProps {
  onUpload: (files: File[]) => void;
  isUploading: boolean;
}

export function DocumentUpload({ onUpload, isUploading }: DocumentUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFiles = useCallback((files: File[]) => {
    setSelectedFiles((previous) => {
      const merged = [...previous, ...files];
      const uniqueByName = new Map<string, File>();
      for (const file of merged) {
        uniqueByName.set(file.name, file);
      }
      return Array.from(uniqueByName.values());
    });
  }, []);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) handleFiles(files);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    if (files.length > 0) handleFiles(files);
  }

  function handleUpload() {
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
          <p className="text-sm text-muted-foreground">
            Drag and drop a file here, or click to select
          </p>
          <input
            ref={inputRef}
            type="file"
            multiple
            onChange={handleChange}
            className="hidden"
            aria-label="Select files"
          />
          <Button
            type="button"
            variant="outline"
            onClick={() => inputRef.current?.click()}
          >
            Select Files
          </Button>
        </div>

        {selectedFiles.length > 0 && (
          <div className="mt-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium">
                {selectedFiles.length} file(s) selected
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
            <Button onClick={handleUpload} disabled={isUploading}>
              {isUploading ? "Uploading..." : "Upload"}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
