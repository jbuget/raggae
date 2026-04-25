import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OrganizationMembersPanel } from "@/components/organizations/organization-members-panel";
import { renderWithProviders } from "../../helpers/render";

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
  useOrganizationInvitations: () => ({ data: [], isLoading: false }),
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

  it("should show no pending invitations message when list is empty", () => {
    renderWithProviders(<OrganizationMembersPanel organizationId="org-1" />);
    expect(screen.getByText("No pending invitations.")).toBeInTheDocument();
  });
});
