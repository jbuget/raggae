import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { SourceBadge } from "@/components/atoms/chat/source-badge";
import { renderWithProviders } from "../../../helpers/render";

describe("SourceBadge", () => {
  it("should render the document name", () => {
    renderWithProviders(<SourceBadge name="rapport-2024.pdf" onClick={vi.fn()} />);
    expect(screen.getByText("rapport-2024.pdf")).toBeInTheDocument();
  });

  it("should render as a button", () => {
    renderWithProviders(<SourceBadge name="doc.pdf" onClick={vi.fn()} />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should call onClick when clicked", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<SourceBadge name="doc.pdf" onClick={onClick} />);
    await user.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledOnce();
  });
});
