import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MobileProjectItem } from "@/components/molecules/sidebar/mobile-project-item";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("next/navigation", () => ({
  usePathname: () => "/projects/proj-1/chat",
}));

const project = {
  id: "proj-1",
  name: "My Project",
  organization_id: null,
} as Parameters<typeof MobileProjectItem>[0]["project"];

describe("MobileProjectItem", () => {
  it("should render project name as a link to chat", () => {
    renderWithProviders(<MobileProjectItem project={project} />);
    expect(screen.getByRole("link", { name: "My Project" })).toHaveAttribute(
      "href",
      "/projects/proj-1/chat",
    );
  });

  it("should apply active styles when pathname is under the project path", () => {
    renderWithProviders(<MobileProjectItem project={project} />);
    expect(screen.getByRole("link", { name: "My Project" })).toHaveClass("bg-primary/10");
  });

  it("should not render any dropdown button", () => {
    renderWithProviders(<MobileProjectItem project={project} />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
