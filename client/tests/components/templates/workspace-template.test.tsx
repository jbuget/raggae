import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WorkspaceTemplate } from "@/components/templates/workspace-template";
import { renderWithProviders } from "../../helpers/render";

describe("WorkspaceTemplate", () => {
  it("should render a single breadcrumb item", () => {
    renderWithProviders(
      <WorkspaceTemplate breadcrumb={[{ label: "My Project" }]}>
        <div>workspace content</div>
      </WorkspaceTemplate>,
    );
    expect(screen.getByText("My Project")).toBeInTheDocument();
  });

  it("should render multiple breadcrumb items with separators", () => {
    renderWithProviders(
      <WorkspaceTemplate
        breadcrumb={[{ label: "My Project" }, { label: "My Conversation" }]}
      >
        <div>workspace content</div>
      </WorkspaceTemplate>,
    );
    expect(screen.getByText("My Project")).toBeInTheDocument();
    expect(screen.getByText("My Conversation")).toBeInTheDocument();
    expect(screen.getByText("›")).toBeInTheDocument();
  });

  it("should render the actions slot", () => {
    renderWithProviders(
      <WorkspaceTemplate
        breadcrumb={[{ label: "My Project" }]}
        actions={<button>Export</button>}
      >
        <div>workspace content</div>
      </WorkspaceTemplate>,
    );
    expect(screen.getByRole("button", { name: "Export" })).toBeInTheDocument();
  });

  it("should render children", () => {
    renderWithProviders(
      <WorkspaceTemplate breadcrumb={[{ label: "My Project" }]}>
        <div>workspace content</div>
      </WorkspaceTemplate>,
    );
    expect(screen.getByText("workspace content")).toBeInTheDocument();
  });
});
