import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SidebarNavLink } from "@/components/layout/sidebar/atoms/sidebar-nav-link";
import { renderWithProviders } from "../../../../helpers/render";

vi.mock("next/navigation", () => ({
  usePathname: () => "/projects",
}));

describe("SidebarNavLink", () => {
  it("should render a link with the correct href and label", () => {
    renderWithProviders(<SidebarNavLink href="/projects" label="Projects" />);
    expect(screen.getByRole("link", { name: "Projects" })).toHaveAttribute("href", "/projects");
  });

  it("should apply active styles when pathname matches exactly", () => {
    renderWithProviders(<SidebarNavLink href="/projects" label="Projects" />);
    expect(screen.getByRole("link", { name: "Projects" })).toHaveClass("bg-primary/10");
  });

  it("should not apply active styles when pathname differs", () => {
    renderWithProviders(<SidebarNavLink href="/organizations" label="Organizations" />);
    expect(screen.getByRole("link", { name: "Organizations" })).not.toHaveClass("bg-primary/10");
  });

  it("should render an icon when provided", () => {
    renderWithProviders(
      <SidebarNavLink href="/projects" label="Projects" icon={<span data-testid="icon" />} />,
    );
    expect(screen.getByTestId("icon")).toBeInTheDocument();
  });

  it("should apply active styles with prefix match when matchPrefix is true", () => {
    renderWithProviders(
      <SidebarNavLink href="/proj" label="Projects" matchPrefix />,
    );
    expect(screen.getByRole("link", { name: "Projects" })).toHaveClass("bg-primary/10");
  });
});
