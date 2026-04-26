import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StatsPage } from "@/components/organisms/stats/stats-page";
import { renderWithProviders } from "../../../helpers/render";

vi.mock("@/lib/hooks/use-auth", () => ({
  useAuth: () => ({ token: "mock-token" }),
}));

vi.mock("@/lib/api/stats", () => ({
  getStats: vi.fn().mockResolvedValue({
    north_star_reliable_answers: 1234,
    generated_at: "2026-01-15T10:00:00Z",
    fonctionnement: {
      indexing_success_rate_percent: 98.5,
      projects_with_documents: 10,
      total_document_size_mb: 42.3,
      total_chunks: 5000,
    },
    usage: {
      users_total: 50,
      users_active_30d: 20,
      organizations_total: 5,
      projects_total: 15,
      projects_published: 8,
      conversations_total: 300,
      messages_total: 1200,
      documents_total: 80,
    },
    impact: {
      reliable_answers_total: 1000,
      reliable_answers_rate_percent: 83.3,
      average_reliability_percent: 90.1,
      relevant_answers_rate_percent: 76.5,
      multi_turn_conversations_rate_percent: 45.2,
      average_sources_per_answer: 3.2,
    },
  }),
}));

describe("StatsPage", () => {
  it("should render the page title", async () => {
    renderWithProviders(<StatsPage />);
    expect(await screen.findByRole("heading", { level: 1 })).toBeInTheDocument();
  });

  it("should display the north star value once data is loaded", async () => {
    renderWithProviders(<StatsPage />);
    expect(await screen.findByText(/1.234/)).toBeInTheDocument();
  });

  it("should display section headings for usage and impact", async () => {
    renderWithProviders(<StatsPage />);
    expect(await screen.findByRole("heading", { level: 2, name: /usage/i })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { level: 2, name: /impact/i })).toBeInTheDocument();
  });
});
