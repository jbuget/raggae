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
  organization_id: null,
  name: "Test Project",
  description: "",
  system_prompt: "",
  is_published: false,
  reindex_status: "idle",
  reindex_progress: 0,
  reindex_total: 0,
  created_at: "2026-01-01T00:00:00Z",
};

const commonHandlers = [
  http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
  http.get("/api/v1/projects/proj-1/configuration", () => HttpResponse.json({
    owner_id: "proj-1",
    embedding_backend: null, embedding_model: null, embedding_api_key_credential_id: null,
    llm_backend: null, llm_model: null, llm_api_key_credential_id: null,
    chunking_strategy: null, parent_child_chunking: null,
    retrieval_strategy: null, retrieval_top_k: null, retrieval_min_score: null,
    reranking_enabled: null, reranker_backend: null, reranker_model: null, reranker_candidate_multiplier: null,
    chat_history_window_size: null, chat_history_max_chars: null,
  })),
  http.get("/api/v1/model-catalog", () => HttpResponse.json({ embedding: {}, llm: {}, reranker: {} })),
  http.get("/api/v1/credentials", () => HttpResponse.json([])),
  http.get("/api/v1/auth/me/project-defaults", () => HttpResponse.json(null)),
  http.get("/api/v1/system/defaults", () => HttpResponse.json(null)),
];

describe("ProjectAdvancedPanel", () => {
  it("should render the embedding models section", async () => {
    server.use(...commonHandlers);
    renderWithProviders(<ProjectAdvancedPanel projectId="proj-1" />);
    expect(await screen.findByRole("button", { name: /Models/i })).toBeInTheDocument();
  });

  it("should render the retrieval section trigger", async () => {
    server.use(...commonHandlers);
    renderWithProviders(<ProjectAdvancedPanel projectId="proj-1" />);
    expect(await screen.findByRole("button", { name: /context retrieval/i })).toBeInTheDocument();
  });

  it("should render the danger zone with delete button", async () => {
    server.use(...commonHandlers);
    renderWithProviders(<ProjectAdvancedPanel projectId="proj-1" />);
    expect(await screen.findByRole("button", { name: /delete/i })).toBeInTheDocument();
  });
});
