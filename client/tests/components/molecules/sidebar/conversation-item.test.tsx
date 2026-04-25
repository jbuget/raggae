import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ConversationItem } from "@/components/molecules/sidebar/conversation-item";
import { renderWithProviders } from "../../../helpers/render";
import type { ConversationResponse } from "@/lib/types/api";

vi.mock("next/navigation", () => ({
  usePathname: vi.fn(() => "/projects/proj-1/chat"),
}));

const conversation: ConversationResponse = {
  id: "conv-1",
  project_id: "proj-1",
  user_id: "user-1",
  created_at: "2024-01-15T10:00:00Z",
  title: "Test conversation",
};

describe("ConversationItem", () => {
  it("should render the conversation link", () => {
    const onDelete = vi.fn();
    renderWithProviders(
      <ConversationItem conversation={conversation} projectId="proj-1" onDelete={onDelete} />,
    );
    expect(screen.getByText("Test conversation")).toBeInTheDocument();
  });

  it("should show context menu button", () => {
    const onDelete = vi.fn();
    renderWithProviders(
      <ConversationItem conversation={conversation} projectId="proj-1" onDelete={onDelete} />,
    );
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should open delete confirmation dialog when delete is clicked", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    renderWithProviders(
      <ConversationItem conversation={conversation} projectId="proj-1" onDelete={onDelete} />,
    );
    await user.click(screen.getByRole("button"));
    await user.click(await screen.findByRole("menuitem"));
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
  });

  it("should call onDelete when confirming deletion", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    renderWithProviders(
      <ConversationItem conversation={conversation} projectId="proj-1" onDelete={onDelete} />,
    );
    await user.click(screen.getByRole("button"));
    await user.click(await screen.findByRole("menuitem"));
    await screen.findByRole("dialog");
    await user.click(screen.getByRole("button", { name: /delete/i }));
    expect(onDelete).toHaveBeenCalledWith("conv-1");
  });

  it("should not call onDelete when cancel is clicked", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    renderWithProviders(
      <ConversationItem conversation={conversation} projectId="proj-1" onDelete={onDelete} />,
    );
    await user.click(screen.getByRole("button"));
    await user.click(await screen.findByRole("menuitem"));
    await screen.findByRole("dialog");
    await user.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onDelete).not.toHaveBeenCalled();
  });
});
