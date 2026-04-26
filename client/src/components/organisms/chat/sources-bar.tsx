"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";

interface MessageSourceDocument {
  documentId: string;
  documentName: string;
  chunkIds: string[];
}

interface SourcesBarProps {
  sources: MessageSourceDocument[];
  onSourceClick: (source: MessageSourceDocument) => void;
}

export function SourcesBar({ sources, onSourceClick }: SourcesBarProps) {
  const t = useTranslations("chat.panel");
  const [isOpen, setIsOpen] = useState(false);

  if (sources.length === 0) return null;

  return (
    <div className="mb-2">
      <Button variant="ghost" size="sm" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? t("hideSources") : t("showSources")} {t("sources")} ({sources.length})
      </Button>
      {isOpen && (
        <div className="mt-2 max-h-48 space-y-2 overflow-y-auto">
          {sources.map((source, i) => (
            <button
              key={source.documentId}
              type="button"
              className="w-full rounded-md bg-muted p-2 text-left text-xs"
              onClick={() => onSourceClick(source)}
            >
              <p className="font-medium">{t("source")} {i + 1}</p>
              <p className="mt-1 line-clamp-1">{source.documentName}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
