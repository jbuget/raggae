import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SidebarNav } from "@/components/organisms/sidebar/sidebar-nav";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("next/navigation", () => ({
  usePathname: () => "/projects",
}));

describe("SidebarNav", () => {
  it("should render links for projects, organizations and invitations", () => {
    renderWithProviders(<SidebarNav />);
    expect(screen.getByRole("link", { name: /projects/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /organizations/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /invitations/i })).toBeInTheDocument();
  });

  it("should highlight the active link based on current pathname", () => {
    renderWithProviders(<SidebarNav />);
    expect(screen.getByRole("link", { name: /projects/i })).toHaveClass("bg-primary/10");
    expect(screen.getByRole("link", { name: /organizations/i })).not.toHaveClass("bg-primary/10");
  });
});
