import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { OrganizationMembersPanel } from "@/components/organisms/organization/organization-members-panel";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "token-1" }),
}));

vi.mock("@/lib/hooks/use-organization-members", () => ({
  useOrganizationMembers: () => ({
    data: [
      {
        id: "member-1",
        organization_id: "org-1",
        user_id: "user-1",
        user_first_name: "John",
        user_last_name: "Owner",
        user_email: "john.owner@example.com",
        role: "owner",
        joined_at: "2024-01-01T00:00:00Z",
      },
      {
        id: "member-2",
        organization_id: "org-1",
        user_id: "user-2",
        user_first_name: "Alice",
        user_last_name: "Doe",
        user_email: "alice.doe@example.com",
        role: "owner",
        joined_at: "2024-02-01T00:00:00Z",
      },
      {
        id: "member-3",
        organization_id: "org-1",
        user_id: "user-3",
        user_first_name: "Bob",
        user_last_name: "Smith",
        user_email: "bob.smith@example.com",
        role: "maker",
        joined_at: "2024-03-01T00:00:00Z",
      },
      {
        id: "member-4",
        organization_id: "org-1",
        user_id: "user-4",
        user_first_name: "Charlie",
        user_last_name: "Brown",
        user_email: "charlie.brown@example.com",
        role: "user",
        joined_at: "2024-04-01T00:00:00Z",
      },
      {
        id: "member-5",
        organization_id: "org-1",
        user_id: "user-5",
        user_first_name: "Zoe",
        user_last_name: "White",
        user_email: "zoe.white@example.com",
        role: "owner",
        joined_at: "2024-05-01T00:00:00Z",
      },
    ],
    isLoading: false,
  }),
  useOrganizationInvitations: () => ({
    data: [
      {
        id: "inv-pending",
        organization_id: "org-1",
        email: "pending@example.com",
        role: "user",
        status: "pending",
        invited_by_user_id: "user-1",
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-06-15T00:00:00Z",
      },
      {
        id: "inv-expired",
        organization_id: "org-1",
        email: "expired@example.com",
        role: "user",
        status: "pending",
        invited_by_user_id: "user-1",
        expires_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
      {
        id: "inv-zoe",
        organization_id: "org-1",
        email: "zoe@example.com",
        role: "user",
        status: "pending",
        invited_by_user_id: "user-1",
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
      {
        id: "inv-alice",
        organization_id: "org-1",
        email: "alice@example.com",
        role: "user",
        status: "pending",
        invited_by_user_id: "user-1",
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
    ],
    isLoading: false,
  }),
  useInviteOrganizationMember: () => ({ mutate: vi.fn(), isPending: false }),
  useUpdateOrganizationMemberRole: () => ({ mutate: vi.fn(), isPending: false }),
  useRemoveOrganizationMember: () => ({ mutate: vi.fn(), isPending: false }),
  useResendOrganizationInvitation: () => ({ mutate: vi.fn(), isPending: false }),
  useRevokeOrganizationInvitation: () => ({ mutate: vi.fn(), isPending: false }),
}));

describe("OrganizationMembersPanel", () => {
  it("should render the member full name", () => {
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    expect(screen.getByText("John Owner")).toBeInTheDocument();
  });

  it("should render the member email", () => {
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    expect(screen.getByText("john.owner@example.com")).toBeInTheDocument();
  });

  it("should display member and invitation counts in section titles", () => {
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    expect(screen.getByText("Current members (5)")).toBeInTheDocument();
    expect(screen.getByText("Pending invitations (4)")).toBeInTheDocument();
  });

  it("should not show expired badge for a pending invitation within validity", () => {
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    const pendingRow = screen.getByText("pending@example.com").closest("div");
    expect(pendingRow?.querySelector("[data-variant=destructive]")).toBeNull();
  });

  it("should show expired badge when invitation expires_at is in the past", () => {
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    const expiredRow = screen.getByText("expired@example.com").closest("div");
    expect(expiredRow).toHaveTextContent("Expired");
  });

  it("should sort current members by role (owner > maker > user) then by name", () => {
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    const expectedOrder = [
      "Alice Doe",
      "John Owner",
      "Zoe White",
      "Bob Smith",
      "Charlie Brown",
    ];
    const nodes = expectedOrder.map((name) => screen.getByText(name));
    for (let i = 0; i < nodes.length - 1; i++) {
      const relation = nodes[i].compareDocumentPosition(nodes[i + 1]);
      expect(relation & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    }
  });

  it("should filter current members by name using the search input", async () => {
    const user = userEvent.setup();
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    const search = screen.getByPlaceholderText("Search by name or email");
    await user.type(search, "alice");
    expect(screen.getByText("Alice Doe")).toBeInTheDocument();
    expect(screen.queryByText("Bob Smith")).not.toBeInTheDocument();
    expect(screen.queryByText("Charlie Brown")).not.toBeInTheDocument();
    expect(screen.queryByText("John Owner")).not.toBeInTheDocument();
    expect(screen.queryByText("Zoe White")).not.toBeInTheDocument();
  });

  it("should filter current members by email using the search input", async () => {
    const user = userEvent.setup();
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    const search = screen.getByPlaceholderText("Search by name or email");
    await user.type(search, "bob.smith");
    expect(screen.getByText("Bob Smith")).toBeInTheDocument();
    expect(screen.queryByText("Alice Doe")).not.toBeInTheDocument();
    expect(screen.queryByText("Charlie Brown")).not.toBeInTheDocument();
  });

  it("should display the last sent date using updated_at instead of created_at", () => {
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    const row = screen.getByText("pending@example.com").closest(".rounded-md");
    const expected = new Date("2024-06-15T00:00:00Z").toLocaleDateString();
    const legacy = new Date("2024-01-01T00:00:00Z").toLocaleDateString();
    expect(row).toHaveTextContent(expected);
    expect(row).not.toHaveTextContent(legacy);
  });

  it("should render pending invitations sorted alphabetically by email", () => {
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    const invitationEmails = [
      "alice@example.com",
      "expired@example.com",
      "pending@example.com",
      "zoe@example.com",
    ];
    const rendered = screen.getAllByText(/@example\.com$/).map((el) => el.textContent);
    const filtered = rendered.filter((email) => email && invitationEmails.includes(email));
    expect(filtered).toEqual(invitationEmails);
  });
});
