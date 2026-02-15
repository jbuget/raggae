import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DocumentUpload } from "@/components/documents/document-upload";
import { renderWithProviders } from "../../helpers/render";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("DocumentUpload", () => {
  it("should render the drop zone", () => {
    renderWithProviders(
      <DocumentUpload onUpload={vi.fn()} isUploading={false} />,
    );

    expect(
      screen.getByText(/drag and drop a file here/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /select file/i }),
    ).toBeInTheDocument();
  });

  it("should show file info after selecting a file", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <DocumentUpload onUpload={vi.fn()} isUploading={false} />,
    );

    const file = new File(["content"], "test.pdf", {
      type: "application/pdf",
    });
    const input = screen.getByLabelText(/select file/i);
    await user.upload(input, file);

    expect(screen.getByText("test.pdf")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /upload/i }),
    ).toBeInTheDocument();
  });

  it("should call onUpload when upload button is clicked", async () => {
    const onUpload = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <DocumentUpload onUpload={onUpload} isUploading={false} />,
    );

    const file = new File(["content"], "test.pdf", {
      type: "application/pdf",
    });
    const input = screen.getByLabelText(/select file/i);
    await user.upload(input, file);
    await user.click(screen.getByRole("button", { name: /^upload$/i }));

    expect(onUpload).toHaveBeenCalledWith(file);
  });

  it("should disable upload button when uploading", async () => {
    const user = userEvent.setup();
    const { rerender } = renderWithProviders(
      <DocumentUpload onUpload={vi.fn()} isUploading={false} />,
    );

    const file = new File(["content"], "test.pdf", {
      type: "application/pdf",
    });
    const input = screen.getByLabelText(/select file/i);
    await user.upload(input, file);

    rerender(
      <DocumentUpload onUpload={vi.fn()} isUploading={true} />,
    );

    expect(
      screen.getByRole("button", { name: /uploading/i }),
    ).toBeDisabled();
  });
});
