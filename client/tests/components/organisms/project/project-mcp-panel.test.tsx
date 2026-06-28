import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProjectMcpPanel } from "@/components/organisms/project/settings/project-mcp-panel";
import type { ProjectMcpActivationViewResponse } from "@/lib/types/api";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

const mockState: {
  views: ProjectMcpActivationViewResponse[];
  isLoading: boolean;
} = { views: [], isLoading: false };

vi.mock("@/lib/hooks/use-project-mcp-activations", () => ({
  useProjectMcpActivations: () => ({
    data: mockState.views,
    isLoading: mockState.isLoading,
  }),
  useActivateProjectMcp: () => ({ mutate: vi.fn(), isPending: false }),
  useDeactivateProjectMcp: () => ({ mutate: vi.fn(), isPending: false }),
}));

function makeView(
  overrides: Partial<ProjectMcpActivationViewResponse> = {},
): ProjectMcpActivationViewResponse {
  const now = new Date().toISOString();
  return {
    org_mcp_server: {
      id: "srv-1",
      organization_id: "org-1",
      name: "Notion",
      slug: "notion",
      url: "https://mcp.notion.test/",
      auth_type: "bearer",
      masked_token: "...wxyz",
      is_active: true,
      tools_snapshot: [
        { name: "search", description: "Search", input_schema: {} },
      ],
      tools_snapshot_at: now,
      timeout_seconds: 30,
      created_at: now,
      updated_at: now,
    },
    is_activated: false,
    ...overrides,
  };
}

describe("ProjectMcpPanel", () => {
  beforeEach(() => {
    mockState.views = [];
    mockState.isLoading = false;
  });

  it("renders title and provider warning", () => {
    renderWithProviders(<ProjectMcpPanel projectId="prj-1" />);
    expect(screen.getByRole("heading", { name: /mcp servers/i })).toBeInTheDocument();
    expect(screen.getByText(/tool calling requires a provider/i)).toBeInTheDocument();
  });

  it("shows the empty state when no MCP server is available", () => {
    renderWithProviders(<ProjectMcpPanel projectId="prj-1" />);
    expect(screen.getByText(/no mcp server is available/i)).toBeInTheDocument();
  });

  it("lists each available server with its activation status", () => {
    mockState.views = [makeView({ is_activated: true })];
    renderWithProviders(<ProjectMcpPanel projectId="prj-1" />);

    expect(screen.getByText("Notion")).toBeInTheDocument();
    expect(screen.getByText("notion")).toBeInTheDocument();
    expect(screen.getByText(/1 tools/i)).toBeInTheDocument();
  });
});
