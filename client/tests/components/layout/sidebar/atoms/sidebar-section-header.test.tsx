import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SidebarSectionHeader } from "@/components/layout/sidebar/atoms/sidebar-section-header";
import { renderWithProviders } from "../../../../helpers/render";

describe("SidebarSectionHeader", () => {
  it("should render the section title", () => {
    renderWithProviders(<SidebarSectionHeader title="My Projects" />);
    expect(screen.getByText("My Projects")).toBeInTheDocument();
  });

  it("should not render create button when canCreate is false", () => {
    renderWithProviders(
      <SidebarSectionHeader
        title="My Projects"
        canCreate={false}
        createHref="/new"
        createAriaLabel="Create"
      />,
    );
    expect(screen.queryByRole("link", { name: "Create" })).not.toBeInTheDocument();
  });

  it("should render create button linking to createHref when canCreate is true", () => {
    renderWithProviders(
      <SidebarSectionHeader
        title="My Projects"
        canCreate
        createHref="/projects?create=1"
        createAriaLabel="Create project"
      />,
    );
    expect(screen.getByRole("link", { name: "Create project" })).toHaveAttribute(
      "href",
      "/projects?create=1",
    );
  });
});
