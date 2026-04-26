import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Header } from "@/components/organisms/layout/header";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/components/organisms/sidebar", () => ({
  MobileSidebar: () => <div data-testid="mobile-sidebar" />,
}));

describe("Header", () => {
  it("should render a header element", () => {
    renderWithProviders(<Header />);
    expect(screen.getByRole("banner")).toBeInTheDocument();
  });

  it("should render a trigger button to open the sheet", () => {
    renderWithProviders(<Header />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should be hidden on medium screens and above (md:hidden)", () => {
    renderWithProviders(<Header />);
    expect(screen.getByRole("banner")).toHaveClass("md:hidden");
  });
});
