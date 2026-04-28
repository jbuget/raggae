import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ViewToggle } from "@/components/atoms/layout/view-toggle";
import { renderWithProviders } from "../../../helpers/render";

describe("ViewToggle", () => {
  it("should render two buttons", () => {
    renderWithProviders(<ViewToggle value="grid" onChange={vi.fn()} />);
    expect(screen.getAllByRole("button")).toHaveLength(2);
  });

  it("should apply aria-label props when provided", () => {
    renderWithProviders(
      <ViewToggle value="grid" onChange={vi.fn()} gridLabel="Grid view" listLabel="List view" />,
    );
    expect(screen.getByRole("button", { name: "Grid view" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "List view" })).toBeInTheDocument();
  });

  it("should call onChange with 'list' when list button is clicked", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <ViewToggle value="grid" onChange={onChange} gridLabel="Grid view" listLabel="List view" />,
    );
    await user.click(screen.getByRole("button", { name: "List view" }));
    expect(onChange).toHaveBeenCalledWith("list");
  });

  it("should call onChange with 'grid' when grid button is clicked", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <ViewToggle value="list" onChange={onChange} gridLabel="Grid view" listLabel="List view" />,
    );
    await user.click(screen.getByRole("button", { name: "Grid view" }));
    expect(onChange).toHaveBeenCalledWith("grid");
  });
});
