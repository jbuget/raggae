import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OrganizationSection } from "@/components/organisms/sidebar/organization-section";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("next/navigation", () => ({
  usePathname: () => "/projects",
  useRouter: vi.fn(() => ({ push: vi.fn() })),
}));

vi.mock("@/lib/hooks/use-chat", () => ({
  useConversations: vi.fn(() => ({ data: [], isLoading: false })),
  useDeleteConversation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: vi.fn(() => ({ token: "fake-token" })),
}));

const organization = {
  id: "org-1",
  name: "Acme Corp",
  slug: null,
  description: null,
  logo_url: null,
  created_by_user_id: "user-1",
  created_at: "2024-01-01",
  updated_at: "2024-01-01",
};

const projects = [
  { id: "p1", name: "Org Project", organization_id: "org-1" },
] as Parameters<typeof OrganizationSection>[0]["projects"];

describe("OrganizationSection", () => {
  it("should render the organization name as section title", () => {
    renderWithProviders(
      <OrganizationSection
        variant="desktop"
        organization={organization}
        projects={projects}
        canCreate
      />,
    );
    expect(screen.getByText("Acme Corp")).toBeInTheDocument();
  });

  it("should show create button with org-specific href when canCreate is true", () => {
    renderWithProviders(
      <OrganizationSection
        variant="desktop"
        organization={organization}
        projects={projects}
        canCreate
      />,
    );
    expect(
      screen.getByRole("link", { name: /create project in acme corp/i }),
    ).toHaveAttribute("href", "/projects?create=1&organizationId=org-1");
  });

  it("should hide create button when canCreate is false", () => {
    renderWithProviders(
      <OrganizationSection
        variant="desktop"
        organization={organization}
        projects={projects}
        canCreate={false}
      />,
    );
    expect(
      screen.queryByRole("link", { name: /create project in/i }),
    ).not.toBeInTheDocument();
  });

  it("should render project toggle buttons", () => {
    renderWithProviders(
      <OrganizationSection
        variant="desktop"
        organization={organization}
        projects={projects}
        canCreate={false}
      />,
    );
    expect(screen.getByRole("button", { name: "Org Project" })).toBeInTheDocument();
  });
});
