import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProjectsSection } from "@/components/organisms/sidebar/projects-section";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("next/navigation", () => ({
  usePathname: () => "/projects",
}));

const projects = [
  { id: "p1", name: "Project Alpha", organization_id: null },
  { id: "p2", name: "Project Beta", organization_id: null },
] as Parameters<typeof ProjectsSection>[0]["projects"];

const baseProps = {
  title: "My Projects",
  canCreate: true,
  createHref: "/projects?create=1",
  createAriaLabel: "Create project",
};

describe("ProjectsSection", () => {
  it("should display loading text when isLoading is true", () => {
    renderWithProviders(
      <ProjectsSection {...baseProps} variant="desktop" projects={[]} isLoading />,
    );
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("should display empty message when there are no projects", () => {
    renderWithProviders(
      <ProjectsSection {...baseProps} variant="desktop" projects={[]} />,
    );
    expect(screen.getByText(/no projects/i)).toBeInTheDocument();
  });

  it("should render project links in desktop variant", () => {
    renderWithProviders(
      <ProjectsSection {...baseProps} variant="desktop" projects={projects} />,
    );
    expect(screen.getByRole("link", { name: "Project Alpha" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Project Beta" })).toBeInTheDocument();
  });

  it("should render project links in mobile variant without dropdown buttons", () => {
    renderWithProviders(
      <ProjectsSection {...baseProps} variant="mobile" projects={projects} />,
    );
    expect(screen.getByRole("link", { name: "Project Alpha" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /project menu/i })).not.toBeInTheDocument();
  });

  it("should show the create button when canCreate is true", () => {
    renderWithProviders(
      <ProjectsSection {...baseProps} variant="desktop" projects={[]} />,
    );
    expect(screen.getByRole("link", { name: "Create project" })).toBeInTheDocument();
  });

  it("should hide the create button when canCreate is false", () => {
    renderWithProviders(
      <ProjectsSection {...baseProps} variant="desktop" projects={[]} canCreate={false} />,
    );
    expect(screen.queryByRole("link", { name: "Create project" })).not.toBeInTheDocument();
  });
});
