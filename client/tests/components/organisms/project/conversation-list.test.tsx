import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ConversationList } from "@/components/organisms/project/conversation-list";
import { renderWithProviders } from "../../../helpers/render";

const mockPush = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
  usePathname: () => "/projects/proj-1/conversations",
}));

const { mockDeleteConversation, mockRenameConversation, mockUseConversations } = vi.hoisted(() => ({
  mockDeleteConversation: vi.fn(),
  mockRenameConversation: vi.fn(),
  mockUseConversations: vi.fn(() => ({
    data: [
      { id: "c1", title: "First conv", created_at: "2026-01-01T10:00:00Z" },
      { id: "c2", title: "Second conv", created_at: "2026-01-02T10:00:00Z" },
      { id: "c3", title: null, created_at: "2026-01-03T10:00:00Z" },
    ],
    isLoading: false,
  })),
}));

vi.mock("@/lib/hooks/use-chat", () => ({
  useConversations: mockUseConversations,
  useDeleteConversation: vi.fn(() => ({ mutate: mockDeleteConversation })),
  useRenameConversation: vi.fn(() => ({ mutate: mockRenameConversation })),
}));

describe("ConversationList", () => {
  it("should render conversation titles", () => {
    renderWithProviders(<ConversationList projectId="proj-1" />);
    expect(screen.getByText("First conv")).toBeInTheDocument();
    expect(screen.getByText("Second conv")).toBeInTheDocument();
  });

  it("should show a 'select all' checkbox in the toolbar", () => {
    renderWithProviders(<ConversationList projectId="proj-1" />);
    expect(screen.getByRole("checkbox", { name: /select all/i })).toBeInTheDocument();
  });

  it("should show individual checkboxes for each conversation", () => {
    renderWithProviders(<ConversationList projectId="proj-1" />);
    expect(screen.getAllByRole("checkbox")).toHaveLength(4); // 1 select-all + 3 items
  });

  it("should select a conversation when its checkbox is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ConversationList projectId="proj-1" />);
    const checkboxes = screen.getAllByRole("checkbox");
    await user.click(checkboxes[1]);
    expect(screen.getByText(/1 selected/i)).toBeInTheDocument();
  });

  it("should show bulk delete button when at least one item is selected", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ConversationList projectId="proj-1" />);
    const checkboxes = screen.getAllByRole("checkbox");
    await user.click(checkboxes[1]);
    expect(screen.getByRole("button", { name: /delete \(1\)/i })).toBeInTheDocument();
  });

  it("should select all when select-all checkbox is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ConversationList projectId="proj-1" />);
    await user.click(screen.getByRole("checkbox", { name: /select all/i }));
    expect(screen.getByText(/3 selected/i)).toBeInTheDocument();
  });

  it("should deselect all when select-all is clicked again", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ConversationList projectId="proj-1" />);
    await user.click(screen.getByRole("checkbox", { name: /select all/i }));
    await user.click(screen.getByRole("checkbox", { name: /select all/i }));
    expect(screen.queryByText(/selected/i)).not.toBeInTheDocument();
  });

  it("should open bulk delete dialog when delete button is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ConversationList projectId="proj-1" />);
    await user.click(screen.getByRole("checkbox", { name: /select all/i }));
    await user.click(screen.getByRole("button", { name: /delete \(3\)/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("should call deleteConversation for each selected item on bulk delete confirm", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ConversationList projectId="proj-1" />);
    await user.click(screen.getByRole("checkbox", { name: /select all/i }));
    await user.click(screen.getByRole("button", { name: /delete \(3\)/i }));
    await user.click(screen.getByRole("button", { name: /^delete$/i }));
    expect(mockDeleteConversation).toHaveBeenCalledTimes(3);
  });

  it("should show empty state when there are no conversations", () => {
    mockUseConversations.mockReturnValueOnce({ data: [], isLoading: false });
    renderWithProviders(<ConversationList projectId="proj-1" />);
    expect(screen.getByText(/no conversations/i)).toBeInTheDocument();
  });
});
