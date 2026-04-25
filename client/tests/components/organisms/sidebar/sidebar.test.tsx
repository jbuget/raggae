import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Sidebar } from "@/components/organisms/sidebar";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("next/navigation", () => ({
  usePathname: () => "/projects/proj-1",
  useRouter: vi.fn(() => ({ push: vi.fn() })),
}));

vi.mock("@/components/organisms/sidebar/use-sidebar-data", () => ({
  useSidebarData: () => ({
    personalProjects: [
      { id: "proj-1", name: "Project One", organization_id: null },
      { id: "proj-2", name: "Project Two", organization_id: null },
    ],
    isLoadingProjects: false,
    sortedOrganizations: [],
    organizationProjectsMap: new Map(),
    editableOrganizationIds: new Set(),
  }),
}));

vi.mock("@/lib/hooks/use-chat", () => ({
  useConversations: vi.fn(() => ({ data: [], isLoading: false })),
  useDeleteConversation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: vi.fn(() => ({ token: "fake-token", user: { id: "user-1" } })),
}));

vi.mock("@/components/organisms/sidebar/user-menu", () => ({
  UserMenu: () => <div data-testid="user-menu" />,
}));

describe("Sidebar", () => {
  it("should render project toggle buttons in sidebar", () => {
    renderWithProviders(<Sidebar />);
    expect(screen.getAllByRole("button", { name: /project one/i }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole("button", { name: /project two/i }).length).toBeGreaterThan(0);
  });

  it("should open project contextual menu with settings link", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Sidebar />);

    await user.click(screen.getByRole("button", { name: /project menu project one/i }));

    expect(screen.getByRole("menuitem", { name: /^settings$/i })).toHaveAttribute(
      "href",
      "/projects/proj-1/settings",
    );
  });
});
