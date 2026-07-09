import { screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AcceptInvitationContent } from "@/components/organisms/organization/accept-invitation-content";
import { renderWithProviders } from "../../../helpers/render";

const mocks = vi.hoisted(() => ({
  auth: {
    token: null as string | null,
    isLoading: false,
  },
  acceptOrganizationInvitation: vi.fn(),
  invalidateQueries: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams("token=abc"),
}));

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => mocks.auth,
}));

vi.mock("@/lib/api/organizations", () => ({
  acceptOrganizationInvitation: mocks.acceptOrganizationInvitation,
}));

vi.mock("@tanstack/react-query", async () => {
  const actual = await vi.importActual<typeof import("@tanstack/react-query")>(
    "@tanstack/react-query",
  );
  return {
    ...actual,
    useQueryClient: () => ({
      invalidateQueries: mocks.invalidateQueries,
    }),
  };
});

describe("AcceptInvitationContent", () => {
  beforeEach(() => {
    mocks.auth.token = null;
    mocks.auth.isLoading = false;
    mocks.acceptOrganizationInvitation.mockReset();
    mocks.invalidateQueries.mockReset();
    mocks.invalidateQueries.mockResolvedValue(undefined);
  });

  it("should show sign in and register links when user is not authenticated", () => {
    renderWithProviders(<AcceptInvitationContent />);

    expect(
      screen.getByText("Sign in or create an account to accept this invitation."),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute(
      "href",
      "/login?callbackUrl=%2Finvitations%2Faccept%3Ftoken%3Dabc",
    );
    expect(screen.getByRole("link", { name: "Create account" })).toHaveAttribute(
      "href",
      "/register?callbackUrl=%2Finvitations%2Faccept%3Ftoken%3Dabc",
    );
  });

  it("should refresh organization caches before showing success", async () => {
    // Given
    mocks.auth.token = "jwt";
    mocks.acceptOrganizationInvitation.mockResolvedValue({
      id: "member-1",
      organization_id: "org-1",
      user_id: "user-1",
      user_first_name: null,
      user_last_name: null,
      user_email: "user@example.com",
      role: "member",
      joined_at: "2026-01-01T00:00:00Z",
    });

    let resolveOrganizationsRefresh: () => void = () => undefined;
    const organizationsRefresh = new Promise<void>((resolve) => {
      resolveOrganizationsRefresh = resolve;
    });
    mocks.invalidateQueries.mockImplementation(({ queryKey }) =>
      queryKey[0] === "organizations" ? organizationsRefresh : Promise.resolve(),
    );

    // When
    renderWithProviders(<AcceptInvitationContent />);

    // Then
    await waitFor(() => {
      expect(mocks.acceptOrganizationInvitation).toHaveBeenCalledWith("jwt", {
        token: "abc",
      });
    });
    await waitFor(() => {
      expect(mocks.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ["organizations"],
        refetchType: "all",
      });
    });
    expect(
      screen.queryByText("Invitation accepted! You have joined the organization."),
    ).not.toBeInTheDocument();

    resolveOrganizationsRefresh();

    expect(
      await screen.findByText("Invitation accepted! You have joined the organization."),
    ).toBeInTheDocument();
    expect(mocks.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ["organizations"],
      refetchType: "all",
    });
    expect(mocks.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ["accessible-projects"],
      refetchType: "all",
    });
    expect(mocks.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ["user-pending-organization-invitations"],
      refetchType: "all",
    });
  });
});
