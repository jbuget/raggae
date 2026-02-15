import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProjectCard } from "@/components/projects/project-card";
import { renderWithProviders } from "../../helpers/render";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/projects",
}));

const mockProject = {
  id: "proj-1",
  user_id: "user-1",
  name: "My Project",
  description: "A great project",
  system_prompt: "",
  is_published: false,
  created_at: "2026-01-15T00:00:00Z",
};

describe("ProjectCard", () => {
  it("should display project name", () => {
    renderWithProviders(<ProjectCard project={mockProject} />);
    expect(screen.getByText("My Project")).toBeInTheDocument();
  });

  it("should display project description", () => {
    renderWithProviders(<ProjectCard project={mockProject} />);
    expect(screen.getByText("A great project")).toBeInTheDocument();
  });

  it("should display created date", () => {
    renderWithProviders(<ProjectCard project={mockProject} />);
    expect(screen.getByText(/Jan 15, 2026/)).toBeInTheDocument();
  });

  it("should link to project detail", () => {
    renderWithProviders(<ProjectCard project={mockProject} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/projects/proj-1");
  });

  it("should show 'No description' when empty", () => {
    renderWithProviders(
      <ProjectCard project={{ ...mockProject, description: "" }} />,
    );
    expect(screen.getByText("No description")).toBeInTheDocument();
  });
});
