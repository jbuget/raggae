import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConversationLink } from "@/components/atoms/sidebar/conversation-link";
import { renderWithProviders } from "../../../helpers/render";
import type { ConversationResponse } from "@/lib/types/api";

vi.mock("next/navigation", () => ({
  usePathname: vi.fn(),
}));

const { usePathname } = await import("next/navigation");

const conversation: ConversationResponse = {
  id: "conv-1",
  project_id: "proj-1",
  user_id: "user-1",
  created_at: "2024-01-15T10:00:00Z",
  title: "My conversation",
};

const conversationNoTitle: ConversationResponse = {
  ...conversation,
  id: "conv-2",
  title: null,
};

describe("ConversationLink", () => {
  it("should render title when conversation has a title", () => {
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1/chat");
    renderWithProviders(<ConversationLink conversation={conversation} projectId="proj-1" />);
    expect(screen.getByText("My conversation")).toBeInTheDocument();
  });

  it("should render formatted date when conversation has no title", () => {
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1/chat");
    renderWithProviders(<ConversationLink conversation={conversationNoTitle} projectId="proj-1" />);
    expect(screen.getByRole("link")).toBeInTheDocument();
    // Should show date-based label (not empty)
    expect(screen.getByRole("link").textContent).not.toBe("");
  });

  it("should link to the correct conversation URL", () => {
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1/chat");
    renderWithProviders(<ConversationLink conversation={conversation} projectId="proj-1" />);
    expect(screen.getByRole("link")).toHaveAttribute(
      "href",
      "/projects/proj-1/chat/conv-1",
    );
  });

  it("should be active when pathname matches conversation id", () => {
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1/chat/conv-1");
    renderWithProviders(<ConversationLink conversation={conversation} projectId="proj-1" />);
    expect(screen.getByRole("link")).toHaveClass("text-primary");
  });

  it("should be inactive when pathname does not match conversation id", () => {
    vi.mocked(usePathname).mockReturnValue("/projects/proj-1/chat/conv-999");
    renderWithProviders(<ConversationLink conversation={conversation} projectId="proj-1" />);
    expect(screen.getByRole("link")).not.toHaveClass("text-primary");
  });
});
