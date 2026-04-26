import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProjectKnowledgePanel } from "@/components/organisms/project/settings/project-knowledge-panel";
import { renderWithProviders } from "../../../../helpers/render";
import { server } from "../../../../helpers/msw-server";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token", user: { id: "user-1" } }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const mockProject = {
  id: "proj-1",
  user_id: "user-1",
  name: "Test Project",
  description: "",
  system_prompt: "",
  is_published: false,
  chunking_strategy: "auto",
  parent_child_chunking: false,
  reindex_status: null,
  created_at: "2026-01-01T00:00:00Z",
};

describe("ProjectKnowledgePanel", () => {
  it("should render the document upload area", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
      http.get("/api/v1/projects/proj-1/documents", () => HttpResponse.json([])),
    );
    renderWithProviders(<ProjectKnowledgePanel projectId="proj-1" />);
    expect(await screen.findByText(/indexed/i)).toBeInTheDocument();
  });

  it("should show empty state when no documents", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
      http.get("/api/v1/projects/proj-1/documents", () => HttpResponse.json([])),
    );
    renderWithProviders(<ProjectKnowledgePanel projectId="proj-1" />);
    expect(await screen.findByText(/no documents yet/i)).toBeInTheDocument();
  });
});
