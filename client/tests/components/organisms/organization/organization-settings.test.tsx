import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { OrganizationSettings } from "@/components/organisms/organization/organization-settings";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => ({ get: () => null, toString: () => "" }),
}));

vi.mock("@/lib/hooks/use-organization", () => ({
  useOrganization: () => ({
    data: {
      id: "org-1",
      name: "Test Org",
      slug: "test-org",
      description: null,
      logo_url: null,
      updated_at: "2026-01-01T00:00:00Z",
    },
    isLoading: false,
    error: null,
  }),
  useUpdateOrganization: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteOrganization: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/lib/hooks/use-organization-members", () => ({
  useOrganizationMembers: () => ({
    data: [{ id: "m1", user_id: "user-1", role: "owner" }],
    isLoading: false,
  }),
  useOrganizationInvitations: () => ({ data: [], isLoading: false }),
  useInviteOrganizationMember: () => ({ mutate: vi.fn(), isPending: false }),
  useUpdateOrganizationMemberRole: () => ({ mutate: vi.fn(), isPending: false }),
  useRemoveOrganizationMember: () => ({ mutate: vi.fn(), isPending: false }),
  useResendOrganizationInvitation: () => ({ mutate: vi.fn(), isPending: false }),
  useRevokeOrganizationInvitation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/lib/hooks/use-org-model-credentials", () => ({
  useOrgModelCredentials: () => ({ data: [], isLoading: false }),
  useCreateOrgModelCredential: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteOrgModelCredential: () => ({ mutate: vi.fn(), isPending: false }),
  useActivateOrgModelCredential: () => ({ mutate: vi.fn(), isPending: false }),
  useDeactivateOrgModelCredential: () => ({ mutate: vi.fn(), isPending: false }),
}));

describe("OrganizationSettings", () => {
  it("should render General, Members and API Keys tabs", () => {
    renderWithProviders(<OrganizationSettings organizationId="org-1" />);
    expect(screen.getByRole("tab", { name: /general/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /members/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /api keys/i })).toBeInTheDocument();
  });

  it("should show OrgCredentialsPanel when API Keys tab is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(<OrganizationSettings organizationId="org-1" />);
    await user.click(screen.getByRole("tab", { name: /api keys/i }));
    expect(screen.getByText(/ai provider api keys/i)).toBeInTheDocument();
  });
});
