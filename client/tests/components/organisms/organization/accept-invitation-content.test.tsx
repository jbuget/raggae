import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AcceptInvitationContent } from "@/components/organisms/organization/accept-invitation-content";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams("token=abc"),
}));

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({
    token: null,
    isLoading: false,
  }),
}));

vi.mock("@/lib/api/organizations", () => ({
  acceptOrganizationInvitation: vi.fn(),
}));

describe("AcceptInvitationContent", () => {
  it("should show sign in and register links when user is not authenticated", () => {
    renderWithProviders(<AcceptInvitationContent />);

    expect(screen.getByText("Sign in or create an account to accept this invitation.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute(
      "href",
      "/login?callbackUrl=%2Finvitations%2Faccept%3Ftoken%3Dabc",
    );
    expect(screen.getByRole("link", { name: "Create account" })).toHaveAttribute(
      "href",
      "/register?callbackUrl=%2Finvitations%2Faccept%3Ftoken%3Dabc",
    );
  });
});
