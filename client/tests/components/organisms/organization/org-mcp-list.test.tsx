import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { OrgMcpList } from "@/components/organisms/organization/org-mcp-list";
import type { OrgMcpServerResponse } from "@/lib/types/api";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

const mockState: { servers: OrgMcpServerResponse[]; isLoading: boolean } = {
  servers: [],
  isLoading: false,
};

vi.mock("@/lib/hooks/use-org-mcp-servers", () => ({
  useOrgMcpServers: () => ({ data: mockState.servers, isLoading: mockState.isLoading }),
  useDeclareOrgMcpServer: () => ({ mutate: vi.fn(), isPending: false }),
  useUpdateOrgMcpServer: () => ({ mutate: vi.fn(), isPending: false }),
  useRefreshOrgMcpTools: () => ({ mutate: vi.fn(), isPending: false }),
  useActivateOrgMcpServer: () => ({ mutate: vi.fn(), isPending: false }),
  useDeactivateOrgMcpServer: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteOrgMcpServer: () => ({ mutate: vi.fn(), isPending: false }),
}));

function makeServer(overrides: Partial<OrgMcpServerResponse> = {}): OrgMcpServerResponse {
  const now = new Date().toISOString();
  return {
    id: "srv-1",
    organization_id: "org-1",
    name: "Notion",
    slug: "notion",
    url: "https://mcp.notion.test/",
    auth_type: "bearer",
    masked_token: "...wxyz",
    is_active: true,
    tools_snapshot: [],
    tools_snapshot_at: now,
    timeout_seconds: 30,
    created_at: now,
    updated_at: now,
    ...overrides,
  };
}

describe("OrgMcpList", () => {
  beforeEach(() => {
    mockState.servers = [];
    mockState.isLoading = false;
  });

  it("renders the panel title and the declare CTA", () => {
    renderWithProviders(<OrgMcpList organizationId="org-1" />);
    expect(screen.getByRole("heading", { name: /mcp servers/i })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /declare a server/i }),
    ).toBeInTheDocument();
  });

  it("shows the empty state when no server is declared", () => {
    renderWithProviders(<OrgMcpList organizationId="org-1" />);
    expect(screen.getByText(/no mcp server declared yet/i)).toBeInTheDocument();
  });

  it("renders a row with name, slug, masked token and tool count", () => {
    mockState.servers = [
      makeServer({
        tools_snapshot: [
          { name: "search", description: "Search docs", input_schema: {} },
          { name: "create_page", description: "Create", input_schema: {} },
        ],
      }),
    ];

    renderWithProviders(<OrgMcpList organizationId="org-1" />);

    expect(screen.getByText("Notion")).toBeInTheDocument();
    expect(screen.getByText("notion")).toBeInTheDocument();
    expect(screen.getByText("...wxyz")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /tools \(2\)/i }),
    ).toBeInTheDocument();
  });

  it("renders the URL of each declared server", () => {
    mockState.servers = [makeServer()];

    renderWithProviders(<OrgMcpList organizationId="org-1" />);

    expect(screen.getByText("https://mcp.notion.test/")).toBeInTheDocument();
  });
});
