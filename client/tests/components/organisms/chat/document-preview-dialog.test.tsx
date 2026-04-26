import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DocumentPreviewDialog } from "@/components/organisms/chat/document-preview-dialog";
import { renderWithProviders } from "../../../helpers/render";

const source = {
  documentId: "doc-1",
  documentName: "rapport.pdf",
  chunkIds: ["chunk-abc"],
};

describe("DocumentPreviewDialog", () => {
  it("should not render when source is null", () => {
    renderWithProviders(
      <DocumentPreviewDialog source={null} documentUrl={null} documentType={null} isLoading={false} error={null} onClose={vi.fn()} />,
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("should render the dialog with the document name when source is provided", () => {
    renderWithProviders(
      <DocumentPreviewDialog source={source} documentUrl={null} documentType={null} isLoading={true} error={null} onClose={vi.fn()} />,
    );
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("rapport.pdf")).toBeInTheDocument();
  });

  it("should show loading text while loading", () => {
    renderWithProviders(
      <DocumentPreviewDialog source={source} documentUrl={null} documentType={null} isLoading={true} error={null} onClose={vi.fn()} />,
    );
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("should show error text when an error occurs", () => {
    renderWithProviders(
      <DocumentPreviewDialog source={source} documentUrl={null} documentType={null} isLoading={false} error="Impossible de charger le document" onClose={vi.fn()} />,
    );
    expect(screen.getByText("Impossible de charger le document")).toBeInTheDocument();
  });

  it("should render chunk ids with copy buttons", () => {
    renderWithProviders(
      <DocumentPreviewDialog source={source} documentUrl={null} documentType={null} isLoading={true} error={null} onClose={vi.fn()} />,
    );
    expect(screen.getByText("chunk-abc")).toBeInTheDocument();
  });

  it("should call onClose when dialog is closed", async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <DocumentPreviewDialog source={source} documentUrl={null} documentType={null} isLoading={true} error={null} onClose={onClose} />,
    );
    await user.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalledOnce();
  });
});
