import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OrgCredentialsPanel } from "@/components/organisms/organization/org-credentials-panel";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

vi.mock("@/lib/hooks/use-org-model-credentials", () => ({
  useOrgModelCredentials: () => ({ data: [], isLoading: false }),
  useCreateOrgModelCredential: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteOrgModelCredential: () => ({ mutate: vi.fn(), isPending: false }),
  useActivateOrgModelCredential: () => ({ mutate: vi.fn(), isPending: false }),
  useDeactivateOrgModelCredential: () => ({ mutate: vi.fn(), isPending: false }),
}));

describe("OrgCredentialsPanel", () => {
  it("should render the panel title", () => {
    renderWithProviders(<OrgCredentialsPanel organizationId="org-1" />);
    expect(screen.getByText(/ai provider api keys/i)).toBeInTheDocument();
  });

  it("should show empty state text when no credentials", () => {
    renderWithProviders(<OrgCredentialsPanel organizationId="org-1" />);
    expect(screen.getAllByText(/no api key saved yet/i).length).toBeGreaterThan(0);
  });

  it("should render an 'Add a key' button", () => {
    renderWithProviders(<OrgCredentialsPanel organizationId="org-1" />);
    expect(screen.getByRole("button", { name: /add a key/i })).toBeInTheDocument();
  });
});
