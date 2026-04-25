from dataclasses import dataclass
from datetime import datetime


@dataclass
class StatsFonctionnementDTO:
    indexing_success_rate_percent: float
    projects_with_documents: int
    total_document_size_mb: float
    total_chunks: int


@dataclass
class StatsUsageDTO:
    users_total: int
    users_active_30d: int
    organizations_total: int
    projects_total: int
    projects_published: int
    conversations_total: int
    messages_total: int
    documents_total: int


@dataclass
class StatsImpactDTO:
    reliable_answers_total: int
    reliable_answers_rate_percent: float
    average_reliability_percent: float
    relevant_answers_rate_percent: float
    multi_turn_conversations_rate_percent: float
    average_sources_per_answer: float


@dataclass
class StatsDTO:
    generated_at: datetime
    north_star_reliable_answers: int
    fonctionnement: StatsFonctionnementDTO
    usage: StatsUsageDTO
    impact: StatsImpactDTO
