import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DocumentRow } from "@/components/documents/document-row";
import { renderWithProviders } from "../../helpers/render";

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
};

describe("DocumentRow", () => {
  it("should display file name", () => {
    renderWithProviders(
      <DocumentRow
        document={mockDoc}
        onDelete={vi.fn()}
        isDeleting={false}
        onReindex={vi.fn()}
        reindexingId={null}
      />,
    );
    expect(screen.getByText("report.pdf")).toBeInTheDocument();
  });

  it("should display file size formatted", () => {
    renderWithProviders(
      <DocumentRow
        document={mockDoc}
        onDelete={vi.fn()}
        isDeleting={false}
        onReindex={vi.fn()}
        reindexingId={null}
      />,
    );
    expect(screen.getByText("2.0 KB")).toBeInTheDocument();
  });

  it("should display created date", () => {
    renderWithProviders(
      <DocumentRow
        document={mockDoc}
        onDelete={vi.fn()}
        isDeleting={false}
        onReindex={vi.fn()}
        reindexingId={null}
      />,
    );
    expect(screen.getByText(/Jan 15, 2026/)).toBeInTheDocument();
  });

  it("should call onDelete after confirmation", async () => {
    const onDelete = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <DocumentRow
        document={mockDoc}
        onDelete={onDelete}
        isDeleting={false}
        onReindex={vi.fn()}
        reindexingId={null}
      />,
    );

    await user.click(screen.getByRole("button", { name: /delete/i }));
    // Confirm in dialog
    const confirmButtons = screen.getAllByRole("button", { name: /delete/i });
    await user.click(confirmButtons[confirmButtons.length - 1]);

    expect(onDelete).toHaveBeenCalledWith("doc-1");
  });
});
