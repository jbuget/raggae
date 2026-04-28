import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DocumentChunksSheet } from "@/components/organisms/document/document-chunks-sheet";
import { renderWithProviders } from "../../../helpers/render";
import { server } from "../../../helpers/msw-server";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token" }),
}));

const mockChunksResponse = {
  document_id: "doc-1",
  processing_strategy: "auto",
  chunks: [
    {
      id: "chunk-1",
      document_id: "doc-1",
      chunk_index: 0,
      content: "First chunk content.",
      created_at: "2026-01-01T00:00:00Z",
      metadata_json: null,
    },
    {
      id: "chunk-2",
      document_id: "doc-1",
      chunk_index: 1,
      content: "Second chunk content.",
      created_at: "2026-01-01T00:00:00Z",
      metadata_json: null,
    },
  ],
};

const defaultProps = {
  projectId: "proj-1",
  documentId: "doc-1",
  documentName: "report.pdf",
  open: true,
  onOpenChange: vi.fn(),
};

describe("DocumentChunksSheet", () => {
  it("should not render content when closed", () => {
    renderWithProviders(<DocumentChunksSheet {...defaultProps} open={false} />);
    expect(screen.queryByText("report.pdf")).not.toBeInTheDocument();
  });

  it("should display document name in sheet title", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/documents/doc-1/chunks", () =>
        HttpResponse.json(mockChunksResponse),
      ),
    );
    renderWithProviders(<DocumentChunksSheet {...defaultProps} />);
    expect(await screen.findByText("report.pdf")).toBeInTheDocument();
  });

  it("should display chunk count in sheet header", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/documents/doc-1/chunks", () =>
        HttpResponse.json(mockChunksResponse),
      ),
    );
    renderWithProviders(<DocumentChunksSheet {...defaultProps} />);
    expect(await screen.findByText(/2/)).toBeInTheDocument();
  });

  it("should display all chunks", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/documents/doc-1/chunks", () =>
        HttpResponse.json(mockChunksResponse),
      ),
    );
    renderWithProviders(<DocumentChunksSheet {...defaultProps} />);
    expect(await screen.findByText("#0")).toBeInTheDocument();
    expect(screen.getByText("#1")).toBeInTheDocument();
  });

  it("should show loading state while fetching", () => {
    server.use(
      http.get("/api/v1/projects/proj-1/documents/doc-1/chunks", async () => {
        await new Promise(() => {});
        return HttpResponse.json({});
      }),
    );
    renderWithProviders(<DocumentChunksSheet {...defaultProps} />);
    expect(screen.getByTestId("chunks-loading")).toBeInTheDocument();
  });

  it("should show empty state when no chunks", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/documents/doc-1/chunks", () =>
        HttpResponse.json({ document_id: "doc-1", processing_strategy: null, chunks: [] }),
      ),
    );
    renderWithProviders(<DocumentChunksSheet {...defaultProps} />);
    expect(await screen.findByTestId("chunks-empty")).toBeInTheDocument();
  });

  it("should show error state when request fails", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/documents/doc-1/chunks", () =>
        HttpResponse.error(),
      ),
    );
    renderWithProviders(<DocumentChunksSheet {...defaultProps} />);
    expect(await screen.findByTestId("chunks-error")).toBeInTheDocument();
  });
});
