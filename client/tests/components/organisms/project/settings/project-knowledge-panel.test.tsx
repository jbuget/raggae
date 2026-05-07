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
  organization_id: null,
  name: "Test Project",
  description: "",
  system_prompt: "",
  is_published: false,
  reindex_status: null,
  reindex_progress: 0,
  reindex_total: 0,
  created_at: "2026-01-01T00:00:00Z",
};

const noEmbeddingConfig = {
  owner_id: "proj-1",
  embedding_backend: null, embedding_model: null, embedding_api_key_credential_id: null,
  llm_backend: null, llm_model: null, llm_api_key_credential_id: null,
  chunking_strategy: null, parent_child_chunking: null,
  retrieval_strategy: null, retrieval_top_k: null, retrieval_min_score: null,
  reranking_enabled: null, reranker_backend: null, reranker_model: null,
  reranker_candidate_multiplier: null, chat_history_window_size: null, chat_history_max_chars: null,
};

const withEmbeddingHandlers = [
  http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
  http.get("/api/v1/projects/proj-1/documents", () => HttpResponse.json([])),
  http.get("/api/v1/projects/proj-1/configuration", () => HttpResponse.json({ ...noEmbeddingConfig, embedding_backend: "gemini" })),
  http.get("/api/v1/auth/me/project-defaults", () => HttpResponse.json(null)),
  http.get("/api/v1/system/defaults", () => HttpResponse.json(null)),
];

describe("ProjectKnowledgePanel", () => {
  it("should render the indexed/total counter", async () => {
    server.use(...withEmbeddingHandlers);
    renderWithProviders(<ProjectKnowledgePanel projectId="proj-1" />);
    expect(await screen.findByText(/0 indexed \/ 0 total/i)).toBeInTheDocument();
  });

  it("should show empty state when no documents", async () => {
    server.use(...withEmbeddingHandlers);
    renderWithProviders(<ProjectKnowledgePanel projectId="proj-1" />);
    expect(await screen.findByText(/no documents yet/i)).toBeInTheDocument();
  });

  it("should not show embedding warning when project config has embedding backend", async () => {
    server.use(...withEmbeddingHandlers);
    renderWithProviders(<ProjectKnowledgePanel projectId="proj-1" />);
    await screen.findByText(/0 indexed \/ 0 total/i);
    expect(screen.queryByText(/no embedding model/i)).not.toBeInTheDocument();
  });

  it("should not show embedding warning when embedding is inherited from user defaults", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
      http.get("/api/v1/projects/proj-1/documents", () => HttpResponse.json([])),
      http.get("/api/v1/projects/proj-1/configuration", () => HttpResponse.json(noEmbeddingConfig)),
      http.get("/api/v1/auth/me/project-defaults", () => HttpResponse.json({ embedding_backend: "gemini" })),
      http.get("/api/v1/system/defaults", () => HttpResponse.json(null)),
    );
    renderWithProviders(<ProjectKnowledgePanel projectId="proj-1" />);
    await screen.findByText(/0 indexed \/ 0 total/i);
    expect(screen.queryByText(/no embedding model/i)).not.toBeInTheDocument();
  });

  it("should not show embedding warning when embedding is inherited from system defaults", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
      http.get("/api/v1/projects/proj-1/documents", () => HttpResponse.json([])),
      http.get("/api/v1/projects/proj-1/configuration", () => HttpResponse.json(noEmbeddingConfig)),
      http.get("/api/v1/auth/me/project-defaults", () => HttpResponse.json(null)),
      http.get("/api/v1/system/defaults", () => HttpResponse.json({ embedding_backend: "gemini" })),
    );
    renderWithProviders(<ProjectKnowledgePanel projectId="proj-1" />);
    await screen.findByText(/0 indexed \/ 0 total/i);
    expect(screen.queryByText(/no embedding model/i)).not.toBeInTheDocument();
  });

  it("should show embedding warning when no embedding configured at any level", async () => {
    server.use(
      http.get("/api/v1/projects/proj-1", () => HttpResponse.json(mockProject)),
      http.get("/api/v1/projects/proj-1/documents", () => HttpResponse.json([])),
      http.get("/api/v1/projects/proj-1/configuration", () => HttpResponse.json(noEmbeddingConfig)),
      http.get("/api/v1/auth/me/project-defaults", () => HttpResponse.json(null)),
      http.get("/api/v1/system/defaults", () => HttpResponse.json({ embedding_backend: null })),
    );
    renderWithProviders(<ProjectKnowledgePanel projectId="proj-1" />);
    expect(await screen.findByText(/no embedding model configured/i)).toBeInTheDocument();
  });
});
