import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ConversationPageItem } from "@/components/molecules/project/conversation-page-item";
import { formatDateTime } from "@/lib/utils/format";
import { renderWithProviders } from "../../../helpers/render";
import type { ConversationResponse } from "@/lib/types/api";

const conversation: ConversationResponse = {
  id: "conv-1",
  project_id: "proj-1",
  user_id: "user-1",
  created_at: "2024-01-15T10:00:00Z",
  title: "Ma conversation",
};

const defaultProps = {
  conversation,
  projectId: "proj-1",
  onDelete: vi.fn(),
  onRename: vi.fn(),
};

describe("ConversationPageItem", () => {
  it("should render the conversation title as a link", () => {
    renderWithProviders(<ConversationPageItem {...defaultProps} />);
    const link = screen.getByRole("link", { name: /ma conversation/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/projects/proj-1/chat/conv-1");
  });

  it("should render the formatted date when title is null", () => {
    const untitled = { ...conversation, title: null };
    renderWithProviders(<ConversationPageItem {...defaultProps} conversation={untitled} />);
    const expected = formatDateTime(untitled.created_at);
    expect(screen.getAllByText(expected).length).toBeGreaterThan(0);
  });

  it("should open rename dialog and call onRename on confirm", async () => {
    const user = userEvent.setup();
    const onRename = vi.fn();
    renderWithProviders(<ConversationPageItem {...defaultProps} onRename={onRename} />);
    await user.click(screen.getByRole("button"));
    const menuItems = await screen.findAllByRole("menuitem");
    await user.click(menuItems.find((i) => i.textContent?.match(/renommer|rename/i))!);
    await screen.findByRole("dialog");
    const input = screen.getByRole("textbox");
    await user.clear(input);
    await user.type(input, "Nouveau titre");
    await user.click(screen.getByRole("button", { name: /enregistrer|save/i }));
    expect(onRename).toHaveBeenCalledWith("conv-1", "Nouveau titre");
  });

  it("should open delete dialog and call onDelete on confirm", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    renderWithProviders(<ConversationPageItem {...defaultProps} onDelete={onDelete} />);
    await user.click(screen.getByRole("button"));
    const menuItems = await screen.findAllByRole("menuitem");
    await user.click(menuItems.find((i) => i.textContent?.match(/supprimer|delete/i))!);
    await screen.findByRole("dialog");
    await user.click(screen.getByRole("button", { name: /supprimer|delete/i }));
    expect(onDelete).toHaveBeenCalledWith("conv-1");
  });

  it("should call onToggleSelect when checkbox is clicked", async () => {
    const user = userEvent.setup();
    const onToggleSelect = vi.fn();
    renderWithProviders(
      <ConversationPageItem {...defaultProps} onToggleSelect={onToggleSelect} />,
    );
    await user.click(screen.getByRole("checkbox"));
    expect(onToggleSelect).toHaveBeenCalledWith("conv-1");
  });
});
