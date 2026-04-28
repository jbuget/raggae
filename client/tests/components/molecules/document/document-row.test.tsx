import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DocumentRow } from "@/components/molecules/document/document-row";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token" }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

const mockDoc = {
  id: "doc-1",
  project_id: "proj-1",
  file_name: "report.pdf",
  content_type: "application/pdf",
  file_size: 2048,
  created_at: "2026-01-15T00:00:00Z",
  processing_strategy: null,
  status: "indexed" as const,
  error_message: null,
  last_indexed_at: null,
};

const defaultProps = {
  chunkingStrategy: "auto" as const,
  parentChildChunking: false,
  onDelete: vi.fn(),
  isDeleting: false,
  onReindex: vi.fn(),
  reindexingId: null,
};

vi.mock("@/components/organisms/document/document-chunks-sheet", () => ({
  DocumentChunksSheet: () => null,
}));

describe("DocumentRow", () => {
  it("should display file name", () => {
    renderWithProviders(<DocumentRow document={mockDoc} {...defaultProps} />);
    expect(screen.getByText("report.pdf")).toBeInTheDocument();
  });

  it("should display file size formatted", () => {
    renderWithProviders(<DocumentRow document={mockDoc} {...defaultProps} />);
    expect(screen.getByText("2.0 KB")).toBeInTheDocument();
  });

  it("should display created date", () => {
    renderWithProviders(<DocumentRow document={mockDoc} {...defaultProps} />);
    expect(screen.getByText(/Jan 15, 2026/)).toBeInTheDocument();
  });

  it("should call onDelete after confirmation", async () => {
    const onDelete = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <DocumentRow document={mockDoc} {...defaultProps} onDelete={onDelete} />,
    );
    await user.click(screen.getByRole("button", { name: /delete/i }));
    const confirmButtons = screen.getAllByRole("button", { name: /delete/i });
    await user.click(confirmButtons[confirmButtons.length - 1]);
    expect(onDelete).toHaveBeenCalledWith("doc-1");
  });

  it("should call onReindex when reindex button is clicked", async () => {
    const onReindex = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <DocumentRow document={mockDoc} {...defaultProps} onReindex={onReindex} />,
    );
    await user.click(screen.getByRole("button", { name: /reindex/i }));
    expect(onReindex).toHaveBeenCalledWith("doc-1");
  });

  it("should disable reindex button when disableReindex is true", () => {
    renderWithProviders(
      <DocumentRow document={mockDoc} {...defaultProps} disableReindex={true} />,
    );
    expect(screen.getByRole("button", { name: /reindex/i })).toBeDisabled();
  });

  it("should display status badge", () => {
    renderWithProviders(<DocumentRow document={mockDoc} {...defaultProps} />);
    expect(screen.getByText("Indexed")).toBeInTheDocument();
  });

  it("should display chunks button", () => {
    renderWithProviders(<DocumentRow document={mockDoc} {...defaultProps} />);
    expect(screen.getByRole("button", { name: /view chunks/i })).toBeInTheDocument();
  });

  it("should enable chunks button when status is indexed", () => {
    renderWithProviders(<DocumentRow document={mockDoc} {...defaultProps} />);
    expect(screen.getByRole("button", { name: /view chunks/i })).not.toBeDisabled();
  });

  it("should disable chunks button when status is not indexed", () => {
    renderWithProviders(
      <DocumentRow document={{ ...mockDoc, status: "uploaded" }} {...defaultProps} />,
    );
    expect(screen.getByRole("button", { name: /view chunks/i })).toBeDisabled();
  });
});
