"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { DocumentChunkResponse } from "@/lib/types/api";

const PREVIEW_LENGTH = 150;

interface ChunkAccordionItemProps {
  chunk: DocumentChunkResponse;
  ariaLabel: string;
  metadataLabel: string;
  parentLabel?: string;
  childLabel?: string;
}

export function ChunkAccordionItem({ 
  chunk, 
  ariaLabel, 
  metadataLabel,
  parentLabel = "Parent",
  childLabel = "Child"
}: ChunkAccordionItemProps) {
  const [expanded, setExpanded] = useState(false);

  const preview =
    chunk.content.length > PREVIEW_LENGTH
      ? chunk.content.slice(0, PREVIEW_LENGTH) + "…"
      : chunk.content;

  const showLevel = chunk.chunk_level === "parent" || chunk.chunk_level === "child";

  return (
    <div className="border-b last:border-b-0">
      <button
        type="button"
        aria-label={ariaLabel}
        aria-expanded={expanded}
        className="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-muted/50 transition-colors"
        onClick={() => setExpanded((prev) => !prev)}
      >
        <div className="flex flex-col items-center gap-1 shrink-0 w-10">
          <span className="font-mono text-xs font-semibold text-muted-foreground">
            #{chunk.chunk_index}
          </span>
          {showLevel && (
            <Badge 
              variant="outline" 
              className={`px-1 py-0 text-[9px] uppercase leading-3 bg-transparent ${
                chunk.chunk_level === "parent" 
                  ? "border-foreground/30 text-foreground font-bold" 
                  : "border-transparent text-muted-foreground"
              }`}
            >
              {chunk.chunk_level === "parent" ? parentLabel : childLabel}
            </Badge>
          )}
        </div>
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
          {(chunk.metadata_json || chunk.parent_chunk_id) && (
            <div data-testid="chunk-metadata">
              <p className="mb-1 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                {metadataLabel}
              </p>
              <pre className="whitespace-pre-wrap break-words rounded-md bg-muted p-3 text-xs font-mono">
                {JSON.stringify({
                  ...chunk.metadata_json,
                  ...(chunk.parent_chunk_id ? { parent_chunk_id: chunk.parent_chunk_id } : {})
                }, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
