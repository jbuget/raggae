import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectSnapshotsList } from "@/components/organisms/project/project-snapshots-list";
import { renderWithProviders } from "../../../helpers/render";
import { server } from "../../../helpers/msw-server";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

const mockSnapshots = [
  {
    id: "snap-1",
    project_id: "proj-1",
    version_number: 2,
    label: "Second snapshot",
    embedding_model: "ada-002",
    llm_model: "gpt-4",
    retrieval_strategy: "hybrid",
    restored_from_version: null,
    created_at: "2026-02-01T00:00:00Z",
  },
  {
    id: "snap-2",
    project_id: "proj-1",
    version_number: 1,
    label: null,
    embedding_model: null,
    llm_model: null,
    retrieval_strategy: "vector",
    restored_from_version: null,
    created_at: "2026-01-01T00:00:00Z",
  },
];

describe("ProjectSnapshotsList", () => {
  it("should render snapshots", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/snapshots", () =>
        HttpResponse.json({ snapshots: mockSnapshots, total: 2 }),
      ),
    );
    renderWithProviders(<ProjectSnapshotsList projectId="proj-1" />);
    expect(await screen.findByText("v2")).toBeInTheDocument();
    expect(screen.getByText("v1")).toBeInTheDocument();
  });

  it("should mark the highest version as current", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/snapshots", () =>
        HttpResponse.json({ snapshots: mockSnapshots, total: 2 }),
      ),
    );
    renderWithProviders(<ProjectSnapshotsList projectId="proj-1" />);
    expect(await screen.findByText("Current version")).toBeInTheDocument();
  });

  it("should show empty state when no snapshots", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/snapshots", () =>
        HttpResponse.json({ snapshots: [], total: 0 }),
      ),
    );
    renderWithProviders(<ProjectSnapshotsList projectId="proj-1" />);
    expect(await screen.findByText(/no versions available/i)).toBeInTheDocument();
  });

  it("should open restore dialog when restore button is clicked", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1/snapshots", () =>
        HttpResponse.json({ snapshots: mockSnapshots, total: 2 }),
      ),
    );
    const user = userEvent.setup();
    renderWithProviders(<ProjectSnapshotsList projectId="proj-1" />);
    await screen.findByText("v2");
    // Click restore on v1 (not current version)
    const restoreButtons = screen.getAllByRole("button", { name: /restore/i });
    const enabledRestore = restoreButtons.find((btn) => !btn.hasAttribute("disabled"));
    await user.click(enabledRestore!);
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
  });
});
