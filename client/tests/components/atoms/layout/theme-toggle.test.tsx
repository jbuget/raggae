import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ThemeToggle } from "@/components/atoms/layout/theme-toggle";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/providers/theme-provider", () => ({
  useTheme: () => ({ theme: "light", setTheme: vi.fn() }),
}));

describe("ThemeToggle", () => {
  it("should render a button", () => {
    renderWithProviders(<ThemeToggle />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should have an accessible aria-label", () => {
    renderWithProviders(<ThemeToggle />);
    expect(screen.getByRole("button")).toHaveAttribute("aria-label");
  });

  it("should call setTheme when clicked", async () => {
    const setTheme = vi.fn();
    vi.mocked(
      await import("@/lib/providers/theme-provider"),
    ).useTheme = vi.fn().mockReturnValue({ theme: "light", setTheme });

    const user = userEvent.setup();
    renderWithProviders(<ThemeToggle />);
    await user.click(screen.getByRole("button"));
    expect(setTheme).toHaveBeenCalledOnce();
  });
});
