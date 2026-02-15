import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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

  it("should open project contextual menu with chat/documents/settings links", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Sidebar />);

    await user.click(screen.getByRole("button", { name: /project menu project one/i }));

    expect(screen.getByRole("menuitem", { name: /^chat$/i })).toHaveAttribute(
      "href",
      "/projects/proj-1/chat",
    );
    expect(screen.getByRole("menuitem", { name: /^documents$/i })).toHaveAttribute(
      "href",
      "/projects/proj-1/documents",
    );
    expect(screen.getByRole("menuitem", { name: /^settings$/i })).toHaveAttribute(
      "href",
      "/projects/proj-1/settings",
    );
  });
});
