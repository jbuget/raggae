import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { SourcesBar } from "@/components/organisms/chat/sources-bar";
import { renderWithProviders } from "../../../helpers/render";

const sources = [
  { documentId: "doc-1", documentName: "rapport-2024.pdf", chunkIds: ["c1"] },
  { documentId: "doc-2", documentName: "contrat.docx", chunkIds: ["c2"] },
];

describe("SourcesBar", () => {
  it("should not render when sources list is empty", () => {
    const { container } = renderWithProviders(
      <SourcesBar sources={[]} onSourceClick={vi.fn()} />,
    );
    expect(container.firstChild).toBeNull();
  });

  it("should render a toggle button with the sources count", () => {
    renderWithProviders(<SourcesBar sources={sources} onSourceClick={vi.fn()} />);
    expect(screen.getByText(/2/)).toBeInTheDocument();
  });

  it("should not show sources by default", () => {
    renderWithProviders(<SourcesBar sources={sources} onSourceClick={vi.fn()} />);
    expect(screen.queryByText("rapport-2024.pdf")).not.toBeInTheDocument();
  });

  it("should show sources after clicking the toggle", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SourcesBar sources={sources} onSourceClick={vi.fn()} />);
    await user.click(screen.getByRole("button"));
    expect(screen.getByText("rapport-2024.pdf")).toBeInTheDocument();
    expect(screen.getByText("contrat.docx")).toBeInTheDocument();
  });

  it("should hide sources after toggling twice", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SourcesBar sources={sources} onSourceClick={vi.fn()} />);
    const toggle = screen.getByRole("button");
    await user.click(toggle);
    await user.click(screen.getAllByRole("button")[0]);
    expect(screen.queryByText("rapport-2024.pdf")).not.toBeInTheDocument();
  });
});
