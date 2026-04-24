import { screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import type { UseMutateFunction } from "@tanstack/react-query";
import { ProjectConversationList } from "@/components/organisms/sidebar/project-conversation-list";
import { renderWithProviders } from "../../../helpers/render";
import type { ConversationResponse } from "@/lib/types/api";

vi.mock("next/navigation", () => ({
  usePathname: vi.fn(),
  useRouter: vi.fn(() => ({ push: vi.fn() })),
}));

vi.mock("@/lib/hooks/use-chat", () => ({
  useConversations: vi.fn(),
  useDeleteConversation: vi.fn(),
}));

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: vi.fn(() => ({ token: "fake-token" })),
}));

const { usePathname } = await import("next/navigation");
const { useConversations, useDeleteConversation } = await import("@/lib/hooks/use-chat");

const makeConversation = (id: string, title: string | null, createdAt: string): ConversationResponse => ({
  id,
  project_id: "proj-1",
  user_id: "user-1",
  created_at: createdAt,
  title,
});

const conversations = [
  makeConversation("conv-1", "First conversation", "2024-01-15T10:00:00Z"),
  makeConversation("conv-2", "Second conversation", "2024-01-16T10:00:00Z"),
  makeConversation("conv-3", "Third conversation", "2024-01-17T10:00:00Z"),
];

const mockDeleteMutation = {
  mutate: vi.fn() as UseMutateFunction<void, Error, string>,
  mutateAsync: vi.fn(),
  isPending: false,
  isIdle: true,
  isSuccess: false,
  isError: false,
  data: undefined,
  error: null,
  reset: vi.fn(),
  status: "idle" as const,
  variables: undefined,
  context: undefined,
  failureCount: 0,
  failureReason: null,
  isPaused: false,
  submittedAt: 0,
};

describe("ProjectConversationList", () => {
  beforeEach(() => {
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1/chat");
    vi.mocked(useDeleteConversation).mockReturnValue(mockDeleteMutation);
  });

  it("should show loading state", () => {
    vi.mocked(useConversations).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      status: "pending",
    } as ReturnType<typeof useConversations>);
    renderWithProviders(<ProjectConversationList projectId="proj-1" />);
    expect(document.querySelectorAll('[data-slot="skeleton"]').length).toBeGreaterThan(0);
  });

  it("should show empty state when no conversations", () => {
    vi.mocked(useConversations).mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      error: null,
      status: "success",
    } as ReturnType<typeof useConversations>);
    renderWithProviders(<ProjectConversationList projectId="proj-1" />);
    expect(screen.getByText(/no conversations/i)).toBeInTheDocument();
  });

  it("should render up to 10 conversations sorted by most recent first", () => {
    const manyConversations = Array.from({ length: 12 }, (_, i) =>
      makeConversation(`conv-${i}`, `Conversation ${i}`, `2024-01-${String(i + 1).padStart(2, "0")}T10:00:00Z`),
    );
    vi.mocked(useConversations).mockReturnValue({
      data: manyConversations,
      isLoading: false,
      isError: false,
      error: null,
      status: "success",
    } as ReturnType<typeof useConversations>);
    renderWithProviders(<ProjectConversationList projectId="proj-1" />);
    const links = screen.getAllByRole("link");
    expect(links.length).toBe(10);
  });

  it("should render conversation titles", () => {
    vi.mocked(useConversations).mockReturnValue({
      data: conversations,
      isLoading: false,
      isError: false,
      error: null,
      status: "success",
    } as ReturnType<typeof useConversations>);
    renderWithProviders(<ProjectConversationList projectId="proj-1" />);
    expect(screen.getByText("First conversation")).toBeInTheDocument();
    expect(screen.getByText("Second conversation")).toBeInTheDocument();
    expect(screen.getByText("Third conversation")).toBeInTheDocument();
  });
});
