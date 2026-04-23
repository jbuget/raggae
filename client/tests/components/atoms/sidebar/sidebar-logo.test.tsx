import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SidebarLogo } from "@/components/atoms/sidebar/sidebar-logo";
import { renderWithProviders } from "../../../helpers/render";

describe("SidebarLogo", () => {
  it("should render a link to /projects with Raggae text", () => {
    renderWithProviders(<SidebarLogo />);
    const link = screen.getByRole("link", { name: /raggae/i });
    expect(link).toHaveAttribute("href", "/projects");
  });
});
