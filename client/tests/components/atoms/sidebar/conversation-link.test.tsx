import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConversationLink } from "@/components/atoms/sidebar/conversation-link";
import { renderWithProviders } from "../../../helpers/render";
import type { ConversationResponse } from "@/lib/types/api";

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
    renderWithProviders(<ConversationLink conversation={conversation} projectId="proj-1" isActive={false} />);
    expect(screen.getByText("My conversation")).toBeInTheDocument();
  });

  it("should render formatted date when conversation has no title", () => {
    renderWithProviders(<ConversationLink conversation={conversationNoTitle} projectId="proj-1" isActive={false} />);
    expect(screen.getByRole("link").textContent).not.toBe("");
  });

  it("should link to the correct conversation URL", () => {
    renderWithProviders(<ConversationLink conversation={conversation} projectId="proj-1" isActive={false} />);
    expect(screen.getByRole("link")).toHaveAttribute("href", "/projects/proj-1/chat/conv-1");
  });

  it("should apply active text style when isActive is true", () => {
    renderWithProviders(<ConversationLink conversation={conversation} projectId="proj-1" isActive={true} />);
    expect(screen.getByRole("link")).toHaveClass("text-primary");
  });

  it("should apply muted text style when isActive is false", () => {
    renderWithProviders(<ConversationLink conversation={conversation} projectId="proj-1" isActive={false} />);
    expect(screen.getByRole("link")).not.toHaveClass("text-primary");
  });
});
