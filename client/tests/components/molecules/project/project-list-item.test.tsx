import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProjectListItem } from "@/components/molecules/project/project-list-item";
import { renderWithProviders } from "../../../helpers/render";
import type { ProjectResponse } from "@/lib/types/api";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

const mockProject = {
  id: "proj-1",
  user_id: "user-1",
  name: "My Project",
  description: "A great project",
  system_prompt: "",
  is_published: false,
  created_at: "2026-01-15T00:00:00Z",
} as ProjectResponse;

describe("ProjectListItem", () => {
  it("should display project name", () => {
    renderWithProviders(<ProjectListItem project={mockProject} />);
    expect(screen.getByText("My Project")).toBeInTheDocument();
  });

  it("should display project description", () => {
    renderWithProviders(<ProjectListItem project={mockProject} />);
    expect(screen.getByText("A great project")).toBeInTheDocument();
  });

  it("should display 'No description' when empty", () => {
    renderWithProviders(<ProjectListItem project={{ ...mockProject, description: "" }} />);
    expect(screen.getByText("No description")).toBeInTheDocument();
  });

  it("should link to project chat", () => {
    renderWithProviders(<ProjectListItem project={mockProject} />);
    expect(screen.getByRole("link")).toHaveAttribute("href", "/projects/proj-1/chat");
  });

  it("should show settings menu when showSettings is true", () => {
    renderWithProviders(<ProjectListItem project={mockProject} showSettings />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should hide settings menu when showSettings is false", () => {
    renderWithProviders(<ProjectListItem project={mockProject} showSettings={false} />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
