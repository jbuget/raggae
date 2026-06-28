from datetime import date, datetime

from pydantic import BaseModel


class StatsFonctionnementResponse(BaseModel):
    indexing_success_rate_percent: float
    projects_with_documents: int
    total_document_size_mb: float
    total_chunks: int


class StatsUsageResponse(BaseModel):
    users_total: int
    users_active_30d: int
    organizations_total: int
    projects_total: int
    projects_published: int
    conversations_total: int
    messages_total: int
    documents_total: int


class StatsImpactResponse(BaseModel):
    reliable_answers_total: int
    reliable_answers_rate_percent: float
    average_reliability_percent: float
    relevant_answers_rate_percent: float
    multi_turn_conversations_rate_percent: float
    average_sources_per_answer: float


class StatsResponse(BaseModel):
    generated_at: datetime
    north_star_reliable_answers: int
    fonctionnement: StatsFonctionnementResponse
    usage: StatsUsageResponse
    impact: StatsImpactResponse


class TimeSeriesPointResponse(BaseModel):
    date: date
    value: int


class StatsTimeSeriesResponse(BaseModel):
    generated_at: datetime
    from_date: date
    to_date: date
    user_messages: list[TimeSeriesPointResponse]
    conversations: list[TimeSeriesPointResponse]
    daily_active_users: list[TimeSeriesPointResponse]
    reliable_answers: list[TimeSeriesPointResponse]
    documents_indexed: list[TimeSeriesPointResponse]
    projects_created: list[TimeSeriesPointResponse]


class McpStatsResponse(BaseModel):
    org_servers_total: int
    org_servers_active: int
    project_activations_active: int
    projects_with_at_least_one_activation: int
