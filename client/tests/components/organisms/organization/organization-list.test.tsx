import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { OrganizationList } from "@/components/organisms/organization/organization-list";
import { renderWithProviders } from "../../../helpers/render";
import { server } from "../../../helpers/msw-server";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  usePathname: () => "/organizations",
  useSearchParams: () => ({ get: () => null }),
}));

const mockOrgs = [
  { id: "org-1", name: "Zebra Corp", slug: "zebra", description: null },
  { id: "org-2", name: "Alpha Corp", slug: "alpha", description: "Great org" },
];

describe("OrganizationList", () => {
  it("should render a list of organizations sorted alphabetically", async () => {
    server.use(
      http.get("/api/v1/organizations", () => HttpResponse.json(mockOrgs)),
      http.get("/api/v1/organizations/:id/members", () => HttpResponse.json([])),
    );
    renderWithProviders(<OrganizationList />);
    const items = await screen.findAllByText(/corp/i);
    expect(items[0]).toHaveTextContent("Alpha Corp");
    expect(items[1]).toHaveTextContent("Zebra Corp");
  });

  it("should show empty state when no organizations", async () => {
    server.use(
      http.get("/api/v1/organizations", () => HttpResponse.json([])),
    );
    renderWithProviders(<OrganizationList />);
    expect(await screen.findByText(/no organizations/i)).toBeInTheDocument();
  });

  it("should open create dialog when ?create=1 is in the URL", async () => {
    vi.mock("next/navigation", () => ({
      useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
      usePathname: () => "/organizations",
      useSearchParams: () => ({ get: (key: string) => (key === "create" ? "1" : null) }),
    }));
    server.use(
      http.get("/api/v1/organizations", () => HttpResponse.json(mockOrgs)),
      http.get("/api/v1/organizations/:id/members", () => HttpResponse.json([])),
    );
    renderWithProviders(<OrganizationList />);
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
  });
});
