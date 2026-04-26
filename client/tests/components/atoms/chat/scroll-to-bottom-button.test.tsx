import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ScrollToBottomButton } from "@/components/atoms/chat/scroll-to-bottom-button";
import { renderWithProviders } from "../../../helpers/render";

describe("ScrollToBottomButton", () => {
  it("should render a button", () => {
    renderWithProviders(<ScrollToBottomButton onClick={vi.fn()} />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should call onClick when clicked", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<ScrollToBottomButton onClick={onClick} />);
    await user.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("should have a rounded-full shape", () => {
    renderWithProviders(<ScrollToBottomButton onClick={vi.fn()} />);
    expect(screen.getByRole("button")).toHaveClass("rounded-full");
  });
});
