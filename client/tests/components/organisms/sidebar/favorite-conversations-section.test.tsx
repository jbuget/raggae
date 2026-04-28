import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { FavoriteConversationsSection } from "@/components/organisms/sidebar/favorite-conversations-section";
import { renderWithProviders } from "../../../helpers/render";
import type { FavoriteConversationResponse } from "@/lib/types/api";

vi.mock("next/navigation", () => ({
  usePathname: vi.fn(() => "/projects/proj-1"),
  useRouter: vi.fn(() => ({ push: vi.fn() })),
}));

vi.mock("@/lib/hooks/use-chat", () => ({
  useFavoriteConversations: vi.fn(),
  useDeleteConversation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useRenameConversation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useToggleFavoriteConversation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: vi.fn(() => ({ token: "fake-token" })),
}));

const { useFavoriteConversations, useToggleFavoriteConversation } = await import(
  "@/lib/hooks/use-chat"
);

const favorite: FavoriteConversationResponse = {
  id: "conv-1",
  project_id: "proj-1",
  project_name: "My Project",
  user_id: "user-1",
  created_at: "2024-01-15T10:00:00Z",
  title: "Favorite Conversation",
  is_favorite: true,
};

describe("FavoriteConversationsSection", () => {
  beforeEach(() => {
    vi.mocked(useFavoriteConversations).mockReturnValue({
      data: [favorite],
      isLoading: false,
    } as unknown as ReturnType<typeof useFavoriteConversations>);
  });

  it("should render nothing when favorites list is empty", () => {
    vi.mocked(useFavoriteConversations).mockReturnValue({
      data: [],
      isLoading: false,
    } as unknown as ReturnType<typeof useFavoriteConversations>);
    const { container } = renderWithProviders(<FavoriteConversationsSection />);
    expect(container).toBeEmptyDOMElement();
  });

  it("should render the conversation title", () => {
    renderWithProviders(<FavoriteConversationsSection />);
    expect(screen.getByText("Favorite Conversation")).toBeInTheDocument();
  });

  it("should not render the project name", () => {
    renderWithProviders(<FavoriteConversationsSection />);
    expect(screen.queryByText("My Project")).not.toBeInTheDocument();
  });

  it("should open rename dialog when rename is clicked in context menu", async () => {
    const user = userEvent.setup();
    renderWithProviders(<FavoriteConversationsSection />);
    await user.click(screen.getByRole("button", { name: /conversation options/i }));
    const menuItems = await screen.findAllByRole("menuitem");
    const renameItem = menuItems.find((item) => item.textContent?.match(/renommer|rename/i));
    await user.click(renameItem!);
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
  });

  it("should call toggleFavorite when remove from favorites is clicked", async () => {
    const toggleFn = vi.fn();
    vi.mocked(useToggleFavoriteConversation).mockReturnValue({
      mutate: toggleFn,
      isPending: false,
    } as unknown as ReturnType<typeof useToggleFavoriteConversation>);

    const user = userEvent.setup();
    renderWithProviders(<FavoriteConversationsSection />);
    await user.click(screen.getByRole("button", { name: /conversation options/i }));
    const menuItems = await screen.findAllByRole("menuitem");
    const favoriteItem = menuItems.find((item) => item.textContent?.match(/retirer|remove/i));
    await user.click(favoriteItem!);
    expect(toggleFn).toHaveBeenCalledWith("conv-1");
  });
});
