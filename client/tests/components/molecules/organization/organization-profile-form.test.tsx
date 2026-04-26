import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { OrganizationProfileForm } from "@/components/molecules/organization/organization-profile-form";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

const defaultProps = {
  organizationId: "org-1",
  initialName: "My Org",
  initialSlug: "my-org",
  initialDescription: "A great org",
  initialLogoUrl: null,
};

describe("OrganizationProfileForm", () => {
  it("should render name, slug, description and logo fields", () => {
    renderWithProviders(<OrganizationProfileForm {...defaultProps} />);
    expect(screen.getByLabelText(/^name$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/slug/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^description$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/logo url/i)).toBeInTheDocument();
  });

  it("should pre-fill fields with initial values", () => {
    renderWithProviders(<OrganizationProfileForm {...defaultProps} />);
    expect(screen.getByLabelText(/^name$/i)).toHaveValue("My Org");
    expect(screen.getByLabelText(/slug/i)).toHaveValue("my-org");
    expect(screen.getByLabelText(/^description$/i)).toHaveValue("A great org");
  });

  it("should disable save button when name is empty", async () => {
    const user = userEvent.setup();
    renderWithProviders(<OrganizationProfileForm {...defaultProps} initialName="" />);
    expect(screen.getByRole("button", { name: /save/i })).toBeDisabled();

    await user.type(screen.getByLabelText(/^name$/i), "New Name");
    expect(screen.getByRole("button", { name: /save/i })).toBeEnabled();
  });
});
