import { apiFetch } from "./client";

export interface StatsFonctionnement {
  indexing_success_rate_percent: number;
  projects_with_documents: number;
  total_document_size_mb: number;
  total_chunks: number;
}

export interface StatsUsage {
  users_total: number;
  users_active_30d: number;
  organizations_total: number;
  projects_total: number;
  projects_published: number;
  conversations_total: number;
  messages_total: number;
  documents_total: number;
}

export interface StatsImpact {
  reliable_answers_total: number;
  reliable_answers_rate_percent: number;
  average_reliability_percent: number;
  relevant_answers_rate_percent: number;
  multi_turn_conversations_rate_percent: number;
  average_sources_per_answer: number;
}

export interface StatsResponse {
  generated_at: string;
  north_star_reliable_answers: number;
  fonctionnement: StatsFonctionnement;
  usage: StatsUsage;
  impact: StatsImpact;
}

export function getStats(token: string): Promise<StatsResponse> {
  return apiFetch<StatsResponse>("/stats", { token });
}
