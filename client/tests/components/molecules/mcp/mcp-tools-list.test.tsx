import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { McpToolsList } from "@/components/molecules/mcp/mcp-tools-list";
import { renderWithProviders } from "../../../helpers/render";

describe("McpToolsList", () => {
  it("shows the empty state when no tool is exposed", () => {
    renderWithProviders(<McpToolsList tools={[]} />);
    expect(
      screen.getByText(/this server does not expose any tool/i),
    ).toBeInTheDocument();
  });

  it("renders one item per tool with name and description", () => {
    renderWithProviders(
      <McpToolsList
        tools={[
          { name: "search", description: "Search documents", input_schema: {} },
          { name: "create_page", description: "Create a page", input_schema: {} },
        ]}
      />,
    );

    expect(screen.getByText("search")).toBeInTheDocument();
    expect(screen.getByText("Search documents")).toBeInTheDocument();
    expect(screen.getByText("create_page")).toBeInTheDocument();
    expect(screen.getByText("Create a page")).toBeInTheDocument();
  });
});
