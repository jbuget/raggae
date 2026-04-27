import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { MobileProjectItem } from "@/components/organisms/sidebar/mobile-project-item";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("next/navigation", () => ({
  usePathname: vi.fn(),
  useRouter: vi.fn(() => ({ push: vi.fn() })),
}));

vi.mock("@/lib/hooks/use-chat", () => ({
  useConversations: vi.fn(() => ({ data: [], isLoading: false })),
  useDeleteConversation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useRenameConversation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useToggleFavoriteConversation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: vi.fn(() => ({ token: "fake-token" })),
}));

const { usePathname } = await import("next/navigation");

const project = {
  id: "proj-1",
  name: "My Project",
  organization_id: null,
} as Parameters<typeof MobileProjectItem>[0]["project"];

describe("MobileProjectItem", () => {
  it("should render project name as a toggle button", () => {
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1");
    renderWithProviders(<MobileProjectItem project={project} />);
    expect(screen.getByRole("button", { name: "My Project" })).toBeInTheDocument();
  });

  it("should not show conversation list initially", () => {
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1");
    renderWithProviders(<MobileProjectItem project={project} />);
    expect(screen.queryByText(/no conversations/i)).not.toBeInTheDocument();
  });

  it("should toggle conversation list when project button is clicked", async () => {
    const user = userEvent.setup();
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1");
    renderWithProviders(<MobileProjectItem project={project} />);
    await user.click(screen.getByRole("button", { name: "My Project" }));
    expect(screen.getByText(/no conversations/i)).toBeInTheDocument();
  });

  it("should close conversation list when clicked again", async () => {
    const user = userEvent.setup();
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1");
    renderWithProviders(<MobileProjectItem project={project} />);
    await user.click(screen.getByRole("button", { name: "My Project" }));
    await user.click(screen.getByRole("button", { name: "My Project" }));
    expect(screen.queryByText(/no conversations/i)).not.toBeInTheDocument();
  });

  it("should apply active styles when pathname is under the project", () => {
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1/chat/conv-1");
    renderWithProviders(<MobileProjectItem project={project} />);
    expect(screen.getByRole("button", { name: "My Project" })).toHaveClass("font-semibold");
  });
});
