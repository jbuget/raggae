import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DesktopProjectItem } from "@/components/layout/sidebar/molecules/desktop-project-item";
import { renderWithProviders } from "../../../../helpers/render";

vi.mock("next/navigation", () => ({
  usePathname: () => "/projects/proj-1/chat",
}));

const project = {
  id: "proj-1",
  name: "My Project",
  organization_id: null,
} as Parameters<typeof DesktopProjectItem>[0]["project"];

describe("DesktopProjectItem", () => {
  it("should render project name as a link to chat", () => {
    renderWithProviders(<DesktopProjectItem project={project} />);
    expect(screen.getByRole("link", { name: "My Project" })).toHaveAttribute(
      "href",
      "/projects/proj-1/chat",
    );
  });

  it("should apply active styles when pathname is under the project path", () => {
    renderWithProviders(<DesktopProjectItem project={project} />);
    const container = screen.getByRole("link", { name: "My Project" }).closest("div");
    expect(container).toHaveClass("bg-primary/10");
  });

  it("should show chat and settings links when dropdown is opened", async () => {
    const user = userEvent.setup();
    renderWithProviders(<DesktopProjectItem project={project} />);

    await user.click(screen.getByRole("button", { name: /project menu/i }));

    expect(screen.getByRole("menuitem", { name: /^chat$/i })).toHaveAttribute(
      "href",
      "/projects/proj-1/chat",
    );
    expect(screen.getByRole("menuitem", { name: /^settings$/i })).toHaveAttribute(
      "href",
      "/projects/proj-1/settings",
    );
  });

  it("should hide settings link when canAccessSettings is false", async () => {
    const user = userEvent.setup();
    renderWithProviders(<DesktopProjectItem project={project} canAccessSettings={false} />);

    await user.click(screen.getByRole("button", { name: /project menu/i }));

    expect(screen.getByRole("menuitem", { name: /^chat$/i })).toBeInTheDocument();
    expect(screen.queryByRole("menuitem", { name: /^settings$/i })).not.toBeInTheDocument();
  });
});
