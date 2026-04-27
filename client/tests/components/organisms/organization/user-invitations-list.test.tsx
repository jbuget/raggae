import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UserInvitationsList } from "@/components/organisms/organization/user-invitations-list";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

const mockInvitations = [
  {
    id: "inv-1",
    organization_id: "org-1",
    organization_name: "Acme Corp",
    role: "user",
    expires_at: new Date(Date.now() + 86400000).toISOString(),
  },
];

vi.mock("@/lib/hooks/use-user-invitations", () => ({
  useUserPendingOrganizationInvitations: vi.fn(),
  useAcceptUserOrganizationInvitation: () => ({ mutate: vi.fn(), isPending: false }),
}));

import { useUserPendingOrganizationInvitations } from "@/lib/hooks/use-user-invitations";

describe("UserInvitationsList", () => {
  it("should display pending invitations", () => {
    vi.mocked(useUserPendingOrganizationInvitations).mockReturnValue({
      data: mockInvitations,
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useUserPendingOrganizationInvitations>);

    renderWithProviders(<UserInvitationsList />);
    expect(screen.getByText("Acme Corp")).toBeInTheDocument();
  });

  it("should show empty state when no invitations", () => {
    vi.mocked(useUserPendingOrganizationInvitations).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useUserPendingOrganizationInvitations>);

    renderWithProviders(<UserInvitationsList />);
    expect(screen.getByText(/no pending invitations/i)).toBeInTheDocument();
  });

  it("should render an accept button per invitation", () => {
    vi.mocked(useUserPendingOrganizationInvitations).mockReturnValue({
      data: mockInvitations,
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useUserPendingOrganizationInvitations>);

    renderWithProviders(<UserInvitationsList />);
    expect(screen.getByRole("button", { name: /accept/i })).toBeInTheDocument();
  });
});
