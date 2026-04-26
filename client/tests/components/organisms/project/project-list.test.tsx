import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectList } from "@/components/organisms/project/project-list";
import { renderWithProviders } from "../../../helpers/render";
import { server } from "../../../helpers/msw-server";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

const mockPush = vi.fn();
const mockReplace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, replace: mockReplace }),
  useSearchParams: () => ({ get: () => null }),
}));

const mockProjects = [
  {
    id: "proj-1",
    user_id: "user-1",
    name: "Alpha",
    description: "First project",
    system_prompt: "",
    is_published: false,
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "proj-2",
    user_id: "user-1",
    name: "Beta",
    description: "",
    system_prompt: "",
    is_published: false,
    created_at: "2026-02-01T00:00:00Z",
  },
];

describe("ProjectList", () => {
  it("should render a list of projects", async () => {
    server.use(
      http.get("/api/v1/projects", () => HttpResponse.json(mockProjects)),
    );
    renderWithProviders(<ProjectList />);
    expect(await screen.findByText("Alpha")).toBeInTheDocument();
    expect(screen.getByText("Beta")).toBeInTheDocument();
  });

  it("should render skeleton while loading", () => {
    server.use(
      http.get("/api/v1/projects", async () => {
        await new Promise(() => {}); // never resolves
        return HttpResponse.json([]);
      }),
    );
    renderWithProviders(<ProjectList />);
    // skeletons are rendered (no project text yet)
    expect(screen.queryByText("Alpha")).not.toBeInTheDocument();
  });

  it("should show empty state when no projects", async () => {
    server.use(
      http.get("/api/v1/projects", () => HttpResponse.json([])),
    );
    renderWithProviders(<ProjectList />);
    expect(await screen.findByText(/no projects yet/i)).toBeInTheDocument();
  });

  it("should open create dialog when ?create=1 is in the URL", async () => {
    vi.mock("next/navigation", () => ({
      useRouter: () => ({ push: mockPush, replace: mockReplace }),
      useSearchParams: () => ({ get: (key: string) => (key === "create" ? "1" : null) }),
    }));
    server.use(
      http.get("/api/v1/projects", () => HttpResponse.json(mockProjects)),
    );
    renderWithProviders(<ProjectList />);
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
  });
});
