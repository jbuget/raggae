import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Sidebar } from "@/components/layout/sidebar";
import { renderWithProviders } from "../../helpers/render";

vi.mock("next/navigation", () => ({
  usePathname: () => "/projects/proj-1",
}));

vi.mock("@/lib/hooks/use-projects", () => ({
  useProjects: () => ({
    data: [
      { id: "proj-1", name: "Project One" },
      { id: "proj-2", name: "Project Two" },
    ],
    isLoading: false,
  }),
}));

describe("Sidebar", () => {
  it("should render project links in sidebar", () => {
    renderWithProviders(<Sidebar />);

    expect(
      screen.getByRole("link", { name: /project one/i }),
    ).toHaveAttribute("href", "/projects/proj-1");
    expect(
      screen.getByRole("link", { name: /project two/i }),
    ).toHaveAttribute("href", "/projects/proj-2");
  });
});
