"use client";

import { useCallback, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { formatFileSize } from "@/lib/utils/format";

interface DocumentUploadProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export function DocumentUpload({ onUpload, isUploading }: DocumentUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFile = useCallback((file: File) => {
    setSelectedFile(file);
  }, []);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  function handleUpload() {
    if (selectedFile) {
      onUpload(selectedFile);
      setSelectedFile(null);
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
            onChange={handleChange}
            className="hidden"
            aria-label="Select file"
          />
          <Button
            type="button"
            variant="outline"
            onClick={() => inputRef.current?.click()}
          >
            Select File
          </Button>
        </div>

        {selectedFile && (
          <div className="mt-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{selectedFile.name}</p>
              <p className="text-xs text-muted-foreground">
                {formatFileSize(selectedFile.size)}
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
