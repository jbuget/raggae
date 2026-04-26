import { screen } from "@testing-library/react";
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
        updated_at: "2024-01-01T00:00:00Z",
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
});
