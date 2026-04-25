import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { NewConversationPicker } from "@/components/organisms/sidebar/new-conversation-picker";
import { renderWithProviders } from "../../../helpers/render";

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
vi.stubGlobal("ResizeObserver", ResizeObserverMock);

const mockPush = vi.fn();
let mockPathname = "/projects";

vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname,
  useRouter: () => ({ push: mockPush }),
}));

vi.mock("@/components/organisms/sidebar/use-sidebar-data", () => ({
  useSidebarData: () => ({
    allProjects: [
      { id: "proj-1", name: "Alpha Project", organization_id: null },
      { id: "proj-2", name: "Beta Project", organization_id: "org-1" },
    ],
    personalProjects: [],
    isLoadingProjects: false,
    sortedOrganizations: [],
    organizationProjectsMap: new Map(),
    editableOrganizationIds: new Set(),
  }),
}));

describe("NewConversationPicker", () => {
  it("should render the trigger button", () => {
    renderWithProviders(<NewConversationPicker />);
    expect(
      screen.getByRole("button", { name: /new conversation/i }),
    ).toBeInTheDocument();
  });

  it("should open the project list on trigger click", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NewConversationPicker />);

    await user.click(screen.getByRole("button", { name: /new conversation/i }));

    expect(screen.getByRole("textbox")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /alpha project/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /beta project/i })).toBeInTheDocument();
  });

  it("should filter projects by search text", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NewConversationPicker />);

    await user.click(screen.getByRole("button", { name: /new conversation/i }));
    await user.type(screen.getByRole("textbox"), "alpha");

    expect(screen.getByRole("button", { name: /alpha project/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /beta project/i })).not.toBeInTheDocument();
  });

  it("should show empty message when no project matches the filter", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NewConversationPicker />);

    await user.click(screen.getByRole("button", { name: /new conversation/i }));
    await user.type(screen.getByRole("textbox"), "zzz");

    expect(screen.queryByRole("button", { name: /alpha project/i })).not.toBeInTheDocument();
    expect(screen.getByText(/no project found/i)).toBeInTheDocument();
  });

  it("should navigate to /projects/{id}/chat on project click and close the popover", async () => {
    const user = userEvent.setup();
    renderWithProviders(<NewConversationPicker />);

    await user.click(screen.getByRole("button", { name: /new conversation/i }));
    await user.click(screen.getByRole("button", { name: /alpha project/i }));

    expect(mockPush).toHaveBeenCalledWith("/projects/proj-1/chat");
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("should highlight the current project when pathname matches", async () => {
    mockPathname = "/projects/proj-1/chat";
    const user = userEvent.setup();
    renderWithProviders(<NewConversationPicker />);

    await user.click(screen.getByRole("button", { name: /new conversation/i }));

    const alphaBtn = screen.getByRole("button", { name: /alpha project/i });
    expect(alphaBtn).toHaveClass("bg-accent");
    const betaBtn = screen.getByRole("button", { name: /beta project/i });
    expect(betaBtn).not.toHaveClass("bg-accent");

    mockPathname = "/projects";
  });
});
