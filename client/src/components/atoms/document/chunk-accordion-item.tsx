"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import type { DocumentChunkResponse } from "@/lib/types/api";

const PREVIEW_LENGTH = 150;

interface ChunkAccordionItemProps {
  chunk: DocumentChunkResponse;
  ariaLabel: string;
  metadataLabel: string;
}

export function ChunkAccordionItem({ chunk, ariaLabel, metadataLabel }: ChunkAccordionItemProps) {
  const [expanded, setExpanded] = useState(false);

  const preview =
    chunk.content.length > PREVIEW_LENGTH
      ? chunk.content.slice(0, PREVIEW_LENGTH) + "…"
      : chunk.content;

  return (
    <div className="border-b last:border-b-0">
      <button
        type="button"
        aria-label={ariaLabel}
        aria-expanded={expanded}
        className="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-muted/50 transition-colors"
        onClick={() => setExpanded((prev) => !prev)}
      >
        <span className="shrink-0 font-mono text-xs font-semibold text-muted-foreground w-8">
          #{chunk.chunk_index}
        </span>
        <span
          data-testid="chunk-preview"
          className="flex-1 text-sm text-muted-foreground line-clamp-2"
        >
          {preview}
        </span>
        <ChevronDown
          className={`shrink-0 size-4 text-muted-foreground transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
        />
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3">
          <pre
            data-testid="chunk-full-content"
            className="whitespace-pre-wrap break-words rounded-md bg-muted p-3 text-xs font-mono"
          >
            {chunk.content}
          </pre>
          {chunk.metadata_json && (
            <div data-testid="chunk-metadata">
              <p className="mb-1 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                {metadataLabel}
              </p>
              <pre className="whitespace-pre-wrap break-words rounded-md bg-muted p-3 text-xs font-mono">
                {JSON.stringify(chunk.metadata_json, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
