import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { CopyButton } from "@/components/atoms/chat/copy-button";
import { renderWithProviders } from "../../../helpers/render";

describe("CopyButton", () => {
  beforeEach(() => {
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      writable: true,
      configurable: true,
    });
  });

  it("should render a copy button", () => {
    renderWithProviders(<CopyButton text="hello" />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should be invisible by default and visible on group hover", () => {
    renderWithProviders(<CopyButton text="hello" />);
    const button = screen.getByRole("button");
    expect(button).toHaveClass("opacity-0");
    expect(button).toHaveClass("group-hover:opacity-100");
  });

  it("should show copy icon initially", () => {
    renderWithProviders(<CopyButton text="hello" />);
    expect(screen.getByTestId("copy-button-copy-icon")).toBeInTheDocument();
  });

  it("should show check icon after click", async () => {
    const user = userEvent.setup();
    renderWithProviders(<CopyButton text="hello" />);
    await user.click(screen.getByRole("button"));
    expect(screen.getByTestId("copy-button-check-icon")).toBeInTheDocument();
  });
});
