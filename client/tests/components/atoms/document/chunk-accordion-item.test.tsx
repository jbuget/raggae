import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ChunkAccordionItem } from "@/components/atoms/document/chunk-accordion-item";
import { renderWithProviders } from "../../../helpers/render";
import type { DocumentChunkResponse } from "@/lib/types/api";

const mockChunk: DocumentChunkResponse = {
  id: "chunk-1",
  document_id: "doc-1",
  chunk_index: 0,
  content: "This is a fairly long chunk content that should be truncated in preview mode when the accordion is collapsed but shown in full when it is expanded by the user.",
  created_at: "2026-01-01T00:00:00Z",
  metadata_json: null,
};

describe("ChunkAccordionItem", () => {
  it("should display chunk index", () => {
    renderWithProviders(<ChunkAccordionItem chunk={mockChunk} />);
    expect(screen.getByText("#0")).toBeInTheDocument();
  });

  it("should display truncated content preview when collapsed", () => {
    renderWithProviders(<ChunkAccordionItem chunk={mockChunk} />);
    const preview = screen.getByTestId("chunk-preview");
    expect(preview).toBeInTheDocument();
    expect(preview.textContent!.length).toBeLessThanOrEqual(153);
  });

  it("should expand to show full content on click", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ChunkAccordionItem chunk={mockChunk} />);
    await user.click(screen.getByRole("button", { name: /chunk #0/i }));
    expect(screen.getByTestId("chunk-full-content")).toBeInTheDocument();
    expect(screen.getByTestId("chunk-full-content").textContent).toBe(mockChunk.content);
  });

  it("should collapse again on second click", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ChunkAccordionItem chunk={mockChunk} />);
    await user.click(screen.getByRole("button", { name: /chunk #0/i }));
    await user.click(screen.getByRole("button", { name: /chunk #0/i }));
    expect(screen.queryByTestId("chunk-full-content")).not.toBeInTheDocument();
  });

  it("should not display metadata section when metadata_json is null", () => {
    renderWithProviders(<ChunkAccordionItem chunk={mockChunk} />);
    expect(screen.queryByTestId("chunk-metadata")).not.toBeInTheDocument();
  });

  it("should display metadata when metadata_json is provided and expanded", async () => {
    const user = userEvent.setup();
    const chunkWithMeta: DocumentChunkResponse = {
      ...mockChunk,
      metadata_json: { section: "Introduction", page: 1 },
    };
    renderWithProviders(<ChunkAccordionItem chunk={chunkWithMeta} />);
    await user.click(screen.getByRole("button", { name: /chunk #0/i }));
    expect(screen.getByTestId("chunk-metadata")).toBeInTheDocument();
  });

  it("should show content without truncation for short content", () => {
    const shortChunk: DocumentChunkResponse = { ...mockChunk, content: "Short." };
    renderWithProviders(<ChunkAccordionItem chunk={shortChunk} />);
    expect(screen.getByTestId("chunk-preview").textContent).toBe("Short.");
  });
});
