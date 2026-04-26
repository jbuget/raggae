import { http, HttpResponse } from "msw";
import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProjectAdvancedPanel } from "@/components/organisms/project/settings/project-advanced-panel";
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
  retrieval_strategy: "hybrid",
  retrieval_top_k: 8,
  retrieval_min_score: 0.3,
  reranking_enabled: false,
  chat_history_window_size: 8,
  chat_history_max_chars: 4000,
  created_at: "2026-01-01T00:00:00Z",
};

describe("ProjectAdvancedPanel", () => {
  it("should render the embedding models section", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
      http.get("/api/v1/projects/proj-1/snapshots", () =>
        HttpResponse.json({ snapshots: [], total: 0 }),
      ),
      http.get("/api/v1/model-catalog", () => HttpResponse.json({ embedding: {}, llm: {}, reranker: {} })),
      http.get("/api/v1/credentials", () => HttpResponse.json([])),
    );
    renderWithProviders(<ProjectAdvancedPanel projectId="proj-1" />);
    expect(await screen.findByRole("heading", { name: /embedding/i })).toBeInTheDocument();
  });

  it("should render the retrieval section heading", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
      http.get("/api/v1/projects/proj-1/snapshots", () =>
        HttpResponse.json({ snapshots: [], total: 0 }),
      ),
      http.get("/api/v1/model-catalog", () => HttpResponse.json({ embedding: {}, llm: {}, reranker: {} })),
      http.get("/api/v1/credentials", () => HttpResponse.json([])),
    );
    renderWithProviders(<ProjectAdvancedPanel projectId="proj-1" />);
    expect(await screen.findByRole("heading", { name: /context retrieval/i })).toBeInTheDocument();
  });

  it("should render the danger zone with delete button", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
      http.get("/api/v1/projects/proj-1/snapshots", () =>
        HttpResponse.json({ snapshots: [], total: 0 }),
      ),
      http.get("/api/v1/model-catalog", () => HttpResponse.json({ embedding: {}, llm: {}, reranker: {} })),
      http.get("/api/v1/credentials", () => HttpResponse.json([])),
    );
    renderWithProviders(<ProjectAdvancedPanel projectId="proj-1" />);
    expect(await screen.findByRole("button", { name: /delete/i })).toBeInTheDocument();
  });
});
