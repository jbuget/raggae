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

const defaultProps = {
  conversation,
  projectId: "proj-1",
  onDelete: vi.fn(),
  onRename: vi.fn(),
};

describe("ConversationItem", () => {
  it("should render the conversation link", () => {
    renderWithProviders(<ConversationItem {...defaultProps} />);
    expect(screen.getByText("Test conversation")).toBeInTheDocument();
  });

  it("should show context menu button", () => {
    renderWithProviders(<ConversationItem {...defaultProps} />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("should open delete confirmation dialog when delete is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ConversationItem {...defaultProps} />);
    await user.click(screen.getByRole("button"));
    const menuItems = await screen.findAllByRole("menuitem");
    const deleteItem = menuItems.find((item) => item.textContent?.match(/supprimer|delete/i));
    await user.click(deleteItem!);
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
  });

  it("should call onDelete when confirming deletion", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    renderWithProviders(<ConversationItem {...defaultProps} onDelete={onDelete} />);
    await user.click(screen.getByRole("button"));
    const menuItems = await screen.findAllByRole("menuitem");
    const deleteItem = menuItems.find((item) => item.textContent?.match(/supprimer|delete/i));
    await user.click(deleteItem!);
    await screen.findByRole("dialog");
    await user.click(screen.getByRole("button", { name: /supprimer|delete/i }));
    expect(onDelete).toHaveBeenCalledWith("conv-1");
  });

  it("should not call onDelete when cancel is clicked", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    renderWithProviders(<ConversationItem {...defaultProps} onDelete={onDelete} />);
    await user.click(screen.getByRole("button"));
    const menuItems = await screen.findAllByRole("menuitem");
    const deleteItem = menuItems.find((item) => item.textContent?.match(/supprimer|delete/i));
    await user.click(deleteItem!);
    await screen.findByRole("dialog");
    await user.click(screen.getByRole("button", { name: /annuler|cancel/i }));
    expect(onDelete).not.toHaveBeenCalled();
  });

  it("should open rename dialog when rename is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ConversationItem {...defaultProps} />);
    await user.click(screen.getByRole("button"));
    const menuItems = await screen.findAllByRole("menuitem");
    const renameItem = menuItems.find((item) => item.textContent?.match(/renommer|rename/i));
    await user.click(renameItem!);
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
  });

  it("should call onRename with trimmed value when confirming rename", async () => {
    const user = userEvent.setup();
    const onRename = vi.fn();
    renderWithProviders(<ConversationItem {...defaultProps} onRename={onRename} />);
    await user.click(screen.getByRole("button"));
    const menuItems = await screen.findAllByRole("menuitem");
    const renameItem = menuItems.find((item) => item.textContent?.match(/renommer|rename/i));
    await user.click(renameItem!);
    await screen.findByRole("dialog");
    const input = screen.getByRole("textbox");
    await user.clear(input);
    await user.type(input, "Nouveau nom");
    await user.click(screen.getByRole("button", { name: /enregistrer|save/i }));
    expect(onRename).toHaveBeenCalledWith("conv-1", "Nouveau nom");
  });
});
