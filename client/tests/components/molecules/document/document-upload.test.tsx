import { fireEvent, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { toast } from "sonner";
import { DocumentUpload } from "@/components/molecules/document/document-upload";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("sonner", () => ({
  toast: Object.assign(vi.fn(), { error: vi.fn(), success: vi.fn() }),
}));

function createDragEvent(files: File[]) {
  return {
    dataTransfer: {
      files,
      items: files.map((file) => ({ kind: "file", type: file.type, getAsFile: () => file })),
      types: ["Files"],
    },
  };
}

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("DocumentUpload", () => {
  it("should render the drop zone with supported formats hint", () => {
    renderWithProviders(<DocumentUpload onUpload={vi.fn()} isUploading={false} />);
    expect(screen.getByText(/drag and drop a file here/i)).toBeInTheDocument();
    expect(screen.getByText(/\.pdf, \.docx, \.pptx, \.txt, \.md, \.csv, \.xlsx, \.xls/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /select files/i })).toBeInTheDocument();
  });

  it("should reject unsupported file formats and show an error toast", () => {
    renderWithProviders(<DocumentUpload onUpload={vi.fn()} isUploading={false} />);
    const zipFile = new File(["content"], "archive.zip", { type: "application/zip" });
    const dropZone = screen.getByTestId("drop-zone");
    fireEvent.drop(dropZone, createDragEvent([zipFile]));
    expect(toast.error).toHaveBeenCalledWith(expect.stringContaining(".zip"));
    expect(screen.queryByText(/1 file\(s\) selected/i)).not.toBeInTheDocument();
  });

  it("should accept supported files and reject unsupported ones in the same drop batch", () => {
    renderWithProviders(<DocumentUpload onUpload={vi.fn()} isUploading={false} />);
    const pdfFile = new File(["content"], "doc.pdf", { type: "application/pdf" });
    const zipFile = new File(["content"], "archive.zip", { type: "application/zip" });
    const dropZone = screen.getByTestId("drop-zone");
    fireEvent.drop(dropZone, createDragEvent([pdfFile, zipFile]));
    expect(toast.error).toHaveBeenCalledWith(expect.stringContaining(".zip"));
    expect(screen.getByText(/1 file\(s\) selected/i)).toBeInTheDocument();
  });

  it("should show file info after selecting a file", async () => {
    const user = userEvent.setup();
    renderWithProviders(<DocumentUpload onUpload={vi.fn()} isUploading={false} />);
    const file = new File(["content"], "test.pdf", { type: "application/pdf" });
    const input = screen.getByLabelText(/select files/i);
    await user.upload(input, file);
    expect(screen.getByText(/1 file\(s\) selected/i)).toBeInTheDocument();
    expect(screen.getByText(/test.pdf/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /upload/i })).toBeInTheDocument();
  });

  it("should call onUpload with file list when upload button is clicked", async () => {
    const onUpload = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<DocumentUpload onUpload={onUpload} isUploading={false} />);
    const file = new File(["content"], "test.pdf", { type: "application/pdf" });
    const input = screen.getByLabelText(/select files/i);
    await user.upload(input, file);
    await user.click(screen.getByRole("button", { name: /^upload$/i }));
    expect(onUpload).toHaveBeenCalledWith([file]);
  });

  it("should disable upload button when uploading", async () => {
    const user = userEvent.setup();
    const { rerender } = renderWithProviders(
      <DocumentUpload onUpload={vi.fn()} isUploading={false} />,
    );
    const file = new File(["content"], "test.pdf", { type: "application/pdf" });
    const input = screen.getByLabelText(/select files/i);
    await user.upload(input, file);
    rerender(<DocumentUpload onUpload={vi.fn()} isUploading={true} />);
    expect(screen.getByRole("button", { name: /uploading/i })).toBeDisabled();
  });

  it("should support selecting multiple files", async () => {
    const user = userEvent.setup();
    renderWithProviders(<DocumentUpload onUpload={vi.fn()} isUploading={false} />);
    const fileOne = new File(["content"], "a.pdf", { type: "application/pdf" });
    const fileTwo = new File(["content"], "b.pdf", { type: "application/pdf" });
    const input = screen.getByLabelText(/select files/i);
    await user.upload(input, [fileOne, fileTwo]);
    expect(screen.getByText(/2 file\(s\) selected/i)).toBeInTheDocument();
    expect(screen.getByText(/a.pdf, b.pdf/i)).toBeInTheDocument();
  });
});
